# Cement Autonomous Ops

Generative AI–driven platform for **autonomous cement plant operations** that optimizes **energy, quality, and sustainability** across raw materials, grinding, clinkerization, utilities, and logistics.

---

## Table of Contents
- [Vision](#vision)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Repo Structure](#repo-structure)
- [Quickstart: Local Prototype](#quickstart-local-prototype)
- [GCP Setup (One-time)](#gcp-setup-one-time)
- [Streaming Pipeline](#streaming-pipeline)
- [Publish Test Data](#publish-test-data)
- [Data Model](#data-model)
- [Roadmap](#roadmap)
- [Safety & Guardrails](#safety--guardrails)
- [Next Steps](#next-steps)

---

## Vision

Build a **Generative AI platform** that:

1. **Ingests** real-time plant data (sensors, SCADA/DCS, ERP, lab).
2. **Optimizes** set-points for energy use, TSR, and quality.
3. **Assists operators** via a Gemini-powered copilot.
4. **Closes the loop** with safe, audited, semi-autonomous control.

---

## Architecture

**Flow: Sources → Ingestion → Storage/Processing → AI & Optimization → Delivery & Control**

- **Sources**: Sensors/IoT, SCADA/DCS tags, Lab/XRF/XRD, ERP
- **Ingestion**: Pub/Sub (stream), Dataflow/Beam (clean/enrich), Batch (GCS → BigQuery)
- **Storage/Processing**: BigQuery (time-series), Cloud Storage (raw), Vertex Pipelines
- **AI**: Predictive models (kiln, mills, quality), Gemini agent, RL/simulations
- **Delivery**: Firebase dashboards, Agent Builder (copilot), Control API to DCS (rate-limited)

---

## Tech Stack

**Google Cloud**
- Pub/Sub, Dataflow (Apache Beam), BigQuery, Cloud Storage
- Vertex AI (training, endpoints, Pipelines), Gemini (Agent Builder)
- Cloud Vision (optional for clinker imagery), Firebase (web UI)

**Languages & Libraries**
- Python 3.10+, Apache Beam, `google-cloud-*`, pandas, scikit-learn
- (Optional) FastAPI for a thin control API

**Ops & Security**
- IAM, Service Accounts, VPC-SC (optional), CMEK (optional), Audit Logs

---

## Repo Structure

```text
cement-autonomous-ops/
│
├── README.md                   # Project overview (this file)
├── .gitignore                  # Python, Node, Terraform ignores
│
├── pipelines/                  # Dataflow / Beam pipelines
│   ├── mini_pipeline_beam.py
│   ├── bq_timeseries_schema.json
│   └── sample_batch.csv
│
├── simulators/                 # Data simulators for Pub/Sub
│   └── pubsub_simulator.py
│
├── infra/                      # Terraform or GCP deployment scripts
│
├── agents/                     # Gemini Copilot / Agent Builder configs
│
├── dashboards/                 # Firebase dashboards
│
└── docs/                       # Documentation, runbooks, ADRs
**Cement Autonomous Ops**

Operational scaffolding for streaming plant telemetry into BigQuery, simulating Pub/Sub data, and preparing dashboards and agents.

**Structure**
- `infra/`: IaC and deployment assets (Terraform, IAM, CI/CD).
- `pipelines/`: Apache Beam pipelines and BigQuery schema.
- `simulators/`: Pub/Sub signal generator for local/dev testing.
- `dashboards/`: Operator UI notes and plans.
- `agents/`: Agent configs, prompts, guardrails.
- `docs/`: Runbooks, ADRs, roadmap.

**Quick Start**
- Install deps: `pip install -r requirements.txt`
- Auth to GCP: `gcloud auth application-default login` (or set `GOOGLE_APPLICATION_CREDENTIALS` to a service account JSON)
- Ensure resources exist:
  - Pub/Sub topic: `projects/YOUR_PROJECT/topics/YOUR_TOPIC`
  - BigQuery dataset and table with schema `pipelines/bq_timeseries_schema.json`

**Run Simulator**
- Edit `simulators/pubsub_simulator.py` and set `PROJECT` and `TOPIC`.
- Start publisher: `python simulators/pubsub_simulator.py`

**Run Beam Pipeline (DirectRunner)**
- Example: `python pipelines/mini_pipeline_beam.py --project YOUR_PROJECT --region YOUR_REGION --input_topic projects/YOUR_PROJECT/topics/YOUR_TOPIC --output_table YOUR_PROJECT:DATASET.TABLE`

**Run on Dataflow (optional)**
- Add runner options, for example:
  - `--runner DataflowRunner --temp_location gs://YOUR_BUCKET/tmp --staging_location gs://YOUR_BUCKET/staging --job_name cement-mini-pipeline`

**BigQuery Schema**
- See `pipelines/bq_timeseries_schema.json` for the canonical table definition.

**Notes**
- The pipeline performs minimal parsing/cleaning; extend `ParseAndClean` for additional validation or enrichment.
- The simulator publishes synthetic tags with light jitter every 2 seconds.
