# TODO

**Infra**
- [ ] Terraform: networks, Pub/Sub topics/subscriptions, BigQuery dataset/table, Dataflow templates.
- [ ] IAM: service accounts and least-privilege roles for pipelines and dashboards.
- [ ] CI/CD: Cloud Build or GitHub Actions for deploy/apply and Dataflow jobs.

**Pipelines**
- [ ] Parameterize schema management (auto-create BQ table from JSON when absent).
- [ ] Add dead-letter handling and error logging.
- [ ] Add windowing and aggregations for downsampling and KPIs.
- [ ] Package pipeline for Dataflow flex templates.
- [ ] Unit tests for `ParseAndClean` and I/O shims.

**Simulators**
- [ ] Add CLI args for project/topic/publish rate.
- [ ] Add random fault injection (spikes, dropouts) and tag profiles.
- [ ] Support CSV replay from `pipelines/sample_batch.csv`.

**Dashboards**
- [ ] Choose stack (Firebase/React) and scaffold.
- [ ] Live charts from BigQuery (e.g., via BQ Storage API or periodic queries).
- [ ] Display model predictions, confidence, and recommendations.
- [ ] Operator approval workflow for safe actions.

**Agents**
- [ ] Define prompt templates and guardrails for kiln/mill copilot.
- [ ] Integrate with plant KPIs and action limits.
- [ ] Logging, observability, and feedback loop.

**Docs**
- [ ] Runbooks for pipeline operations and troubleshooting.
- [ ] Architecture diagram and ADRs.
- [ ] Roadmap with milestones.

**Dev Experience**
- [ ] Makefile with `simulate`, `pipeline`, and `deploy` targets.
- [ ] Pre-commit hooks and formatting (e.g., black, isort).

**Roadmap**
- Phase 0: Data plumbing
  - [ ] Pub/Sub → BigQuery baseline in place
  - [ ] Data quality checks + DLQ wiring
  - [ ] Basic dashboard with live tags
- Phase 1: KPI baselines
  - [ ] Windowed KPIs (1/5/15-min), deviations, alerts
  - [ ] Shift report views and exports
- Phase 2: Copilot
  - [ ] Gemini guidance with guardrails and citations
  - [ ] Human-in-the-loop approval workflow
- Phase 3: Closed-loop
  - [ ] Constrained setpoint optimizer (safe bounds)
  - [ ] Staged rollout and monitoring

**Data Model (BigQuery)**
- [ ] `timeseries_raw` (exists) — validate partitioning/clustering
- [ ] `lab_results` — schema + batch loader
- [ ] `fuel_mix_events` — schema + loader
- [ ] `setpoints_actions` — schema + API surface
- [ ] `maintenance_events` — schema + loader
- [ ] `production_log` — schema + loader

**Pipelines (details)**
- Streaming
  - [ ] Side outputs for DQ (bad JSON, missing fields)
  - [ ] Dead-letter queue (Pub/Sub or BQ table)
  - [ ] Windowed aggregations (1/5/15-min), rolling means, deltas, SPC limits
- Batch
  - [ ] Historian/CSV loaders for lab and production logs
- Views
  - [ ] “Gold” views joined/aligned for dashboards and agents

**Models**
- [ ] Forecasting (tag/KPI level: Prophet/ARIMA/XGBoost)
- [ ] Anomaly detection (autoencoder/density-based)
- [ ] Quality prediction (raw meal/clinker properties from process tags)
- [ ] Optimizer prototype (multi-objective with constraints)

**Agents (capabilities)**
- [ ] Operator Copilot: explain deviations, propose safe corrections
- [ ] Cross-Process Optimizer: coordinated setpoints across kiln/mills/utilities
- [ ] Guardrails: hard limits, SOPs, interlocks, approvals

**Dashboards (views)**
- [ ] Shift view: live KPIs, alerts, recommendations + approvals
- [ ] Quality tracker: raw meal/clinker trends vs specs
- [ ] Energy & TSR: consumption, AF blend tracking, targets vs actuals

**Infra & CI/CD**
- [ ] Terraform skeleton: Pub/Sub, BigQuery, service accounts, IAM
- [ ] GitHub Actions/Cloud Build: IaC apply + Dataflow templates
- [ ] Security: least-privilege IAM, secret management
- [ ] Observability: Cloud Logging, Error Reporting, metrics

**Schemas & Views**
- [ ] JSON schemas for: `lab_results`, `fuel_mix_events`, `setpoints_actions`, `maintenance_events`, `production_log`
- [ ] Materialized views for shift KPIs and quality joins

**Dev Experience (extras)**
- [ ] Makefile targets: `simulate`, `pipeline`, `deploy`, `bq-init`
- [ ] `.env.example` and config loader
- [ ] Dev container/Docker for reproducible runs
