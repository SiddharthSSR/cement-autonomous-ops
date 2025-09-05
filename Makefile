-include .env
activate:
	python3 -m venv venv && . venv/bin/activate && pip install -U pip && pip install -r requirements.txt
gcloud-login:
	gcloud auth application-default login
enable-apis:
	gcloud services enable bigquery.googleapis.com pubsub.googleapis.com dataflow.googleapis.com aiplatform.googleapis.com storage.googleapis.com
bq-init:
	bq mk --dataset --location=$(REGION) $(PROJECT):$(BQ_DATASET) || true
	bq mk --table $(PROJECT):$(BQ_DATASET).$(BQ_TABLE) 'ts:TIMESTAMP,tag:STRING,value:FLOAT,unit:STRING,equipment:STRING,line:STRING,quality_context:STRING' || true
topics:
	gcloud pubsub topics create $(TOPIC) --project $(PROJECT) || true
	gcloud pubsub topics create $(DLQ_TOPIC) --project $(PROJECT) || true
sim:
	python simulators/pubsub_simulator.py
beam-local:
	python pipelines/mini_pipeline_beam.py \
	  --project $(PROJECT) --region $(REGION) \
	  --input_topic projects/$(PROJECT)/topics/$(TOPIC) \
	  --output_table $(PROJECT).$(BQ_DATASET).$(BQ_TABLE) \
	  --runner DirectRunner
beam-dataflow:
	python pipelines/mini_pipeline_beam.py \
	  --project $(PROJECT) --region $(REGION) \
	  --input_topic projects/$(PROJECT)/topics/$(TOPIC) \
	  --output_table $(PROJECT).$(BQ_DATASET).$(BQ_TABLE) \
	  --runner DataflowRunner \
	  --temp_location $(BUCKET)/tmp --staging_location $(BUCKET)/staging \
	  --job_name cement-mini-pipeline
