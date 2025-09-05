"""
Mini streaming pipeline: Pub/Sub (JSON) -> clean/enrich -> BigQuery
"""
import json
import argparse
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions


class ParseAndClean(beam.DoFn):
    def process(self, element):
        s = element.decode("utf-8") if isinstance(element, (bytes, bytearray)) else element
        try:
            row = json.loads(s)
        except Exception:
            return
        ts, tag = row.get("ts"), row.get("tag")
        if not ts or not tag:
            return
        try:
            value = float(row.get("value")) if row.get("value") is not None else None
        except Exception:
            value = None
        yield {
            "ts": ts,
            "tag": tag,
            "value": value,
            "unit": row.get("unit"),
            "equipment": row.get("equipment"),
            "line": row.get("line"),
            "quality_context": row.get("quality_context"),
        }


def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True)
    parser.add_argument("--region", required=True)
    parser.add_argument("--input_topic", required=True)
    parser.add_argument("--output_table", required=True)
    args, pipeline_args = parser.parse_known_args(argv)

    opts = PipelineOptions(pipeline_args, save_main_session=True, streaming=True)
    opts.view_as(StandardOptions).streaming = True

    with beam.Pipeline(options=opts) as p:
        (
            p
            | "ReadPubSub" >> beam.io.ReadFromPubSub(topic=args.input_topic)
            | "ParseClean" >> beam.ParDo(ParseAndClean())
            | "WriteBQ" >> beam.io.WriteToBigQuery(
                args.output_table,
                schema="ts:TIMESTAMP,tag:STRING,value:FLOAT,unit:STRING,equipment:STRING,line:STRING,quality_context:STRING",
                create_disposition=beam.io.BigQueryDisposition.CREATE_NEVER,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            )
        )


if __name__ == "__main__":
    run()
