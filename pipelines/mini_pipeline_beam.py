"""
Pub/Sub (JSON) -> clean/enrich -> BigQuery (streaming inserts)
- Use ONE of: --input_topic OR --input_subscription
- Invalid rows -> Pub/Sub DLQ (if provided)
- Normalizes 'ts' to RFC3339 Z (BigQuery TIMESTAMP friendly)
"""

from __future__ import annotations

import json
import logging
import argparse
from datetime import datetime, timezone
from typing import Optional, Union, Generator, Any

import apache_beam as beam
from apache_beam.pipeline import Pipeline  # runtime export is OK; helps readability
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from apache_beam.pvalue import TaggedOutput

# Public I/O transforms (avoid beam.io.* for type-checkers)
from apache_beam.io.gcp.pubsub import ReadFromPubSub, WriteToPubSub
from apache_beam.io.gcp.bigquery import WriteToBigQuery, BigQueryDisposition


BQ_SCHEMA = (
    "ts:TIMESTAMP,tag:STRING,value:FLOAT,unit:STRING,"
    "equipment:STRING,line:STRING,quality_context:STRING"
)


def to_rfc3339(ts: Optional[str]) -> Optional[str]:
    """Accepts '2025-09-06T06:00:00Z' or '2025-09-06 06:00:00', returns RFC3339 Z or None."""
    if not ts:
        return None
    # try ISO first (with Z or offset)
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        dt = None
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
            try:
                dt = datetime.strptime(ts, fmt).replace(tzinfo=timezone.utc)
                break
            except ValueError:
                continue
        if dt is None:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class ParseAndClean(beam.DoFn):
    """
    Parses Pub/Sub message bytes -> dict, validates & normalizes.
    Emits main output rows OR a 'dlq' side output (bytes) with error context.
    """

    def __init__(self, enable_dlq: bool = False):
        self.enable_dlq = enable_dlq

    def _emit_dlq(self, reason: str, payload: str) -> Optional[TaggedOutput]:
        logging.warning("Dropped message (%s): %s", reason, payload[:500])
        if self.enable_dlq:
            # Produce a bytes message for WriteToPubSub
            return TaggedOutput(
                "dlq",
                json.dumps({"error": reason, "payload": payload}).encode("utf-8"),
            )
        return None

    def process(self, element: bytes) -> Generator[Union[dict[str, Any], TaggedOutput], None, None]:
        raw = element.decode("utf-8") if isinstance(element, (bytes, bytearray)) else str(element)
        try:
            row = json.loads(raw)
        except Exception as e:  # bad JSON
            out = self._emit_dlq(f"bad_json:{e}", raw)
            if out is not None:
                yield out
            return

        ts = to_rfc3339(row.get("ts"))
        tag = row.get("tag")
        if not ts or not tag:
            out = self._emit_dlq("missing_fields_ts_or_tag", raw)
            if out is not None:
                yield out
            return

        # numeric coercion
        val = row.get("value")
        try:
            value = float(val) if val is not None else None
        except Exception:
            value = None

        # guardrails (examples)
        if tag.startswith("kiln.") and value is not None and not (200 <= value <= 2000):
            out = self._emit_dlq("kiln_value_out_of_bounds", raw)
            if out is not None:
                yield out
            return
        if tag.endswith(".motor_power") and value is not None and value < 0:
            out = self._emit_dlq("negative_motor_power", raw)
            if out is not None:
                yield out
            return

        yield {
            "ts": ts,
            "tag": tag,
            "value": value,
            "unit": row.get("unit"),
            "equipment": row.get("equipment"),
            "line": row.get("line"),
            "quality_context": row.get("quality_context"),
        }


def run(argv=None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--region", required=True)

    # Choose one
    parser.add_argument("--input_topic", help="projects/<PROJECT>/topics/<TOPIC>")
    parser.add_argument("--input_subscription", help="projects/<PROJECT>/subscriptions/<SUBSCRIPTION>")

    parser.add_argument(
        "--output_table",
        required=True,
        help="BigQuery table: PROJECT:DATASET.TABLE (also accepts PROJECT.DATASET.TABLE)",
    )
    parser.add_argument("--dlq_topic", help="projects/<PROJECT>/topics/<DLQ_TOPIC>", default=None)

    args, pipeline_args = parser.parse_known_args(argv)

    if bool(args.input_topic) == bool(args.input_subscription):
        raise SystemExit("Provide exactly ONE of --input_topic or --input_subscription")

    # Streaming
    options = PipelineOptions(pipeline_args, save_main_session=True, streaming=True)
    options.view_as(StandardOptions).streaming = True

    def _normalize_table_spec(table: str) -> str:
        """Normalize BigQuery table spec.

        Accepts one of:
        - PROJECT:DATASET.TABLE (preferred)
        - PROJECT.DATASET.TABLE (normalized to PROJECT:DATASET.TABLE)
        - DATASET.TABLE (uses default project from options)
        """
        if ":" in table:
            return table
        parts = table.split(".")
        if len(parts) == 3:
            # PROJECT.DATASET.TABLE -> PROJECT:DATASET.TABLE
            project, dataset, tbl = parts
            return f"{project}:{dataset}.{tbl}"
        return table

    normalized_output_table = _normalize_table_spec(args.output_table)

    with Pipeline(options=options) as p:
        # Read
        if args.input_subscription:
            messages = p | "ReadFromSubscription" >> ReadFromPubSub(subscription=args.input_subscription)
        else:
            messages = p | "ReadFromTopic" >> ReadFromPubSub(topic=args.input_topic)

        # Parse & clean with side output
        outputs = (
            messages
            | "ParseClean"
            >> beam.ParDo(ParseAndClean(enable_dlq=bool(args.dlq_topic))).with_outputs("dlq", main="rows")
        )
        rows = outputs.rows
        dlq_msgs = outputs.dlq

        # Write to BigQuery (public API, streaming inserts)
        _ = (
            rows
            | "WriteToBQ"
            >> WriteToBigQuery(
                normalized_output_table,
                schema=BQ_SCHEMA,
                create_disposition=BigQueryDisposition.CREATE_IF_NEEDED,
                write_disposition=BigQueryDisposition.WRITE_APPEND,
                method=WriteToBigQuery.Method.STREAMING_INSERTS,
                # insert_retry_strategy kept default (retry transient errors)
            )
        )

        # Publish DLQ messages (if a topic is provided)
        if args.dlq_topic:
            _ = dlq_msgs | "PublishDLQ" >> WriteToPubSub(topic=args.dlq_topic)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    run()
