#!/usr/bin/env bash

# Enable necessary GCP services
gcloud services enable aiplatform.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable bigquerydatatransfer.googleapis.com

# Copy public dataset (if necessary)
bq mk --force=true --dataset Your_dataset
bq mk \
  --transfer_config \
  --data_source=cross_region_copy \
  --target_dataset = Your_dataset \
  --display_name='SQL Talk Sample Data' \
  --schedule_end_time="$(date -u -d '5 mins' +%Y-%m-%dT%H:%M:%SZ)" \
  --params='{
      "source_project_id":"project_id",
      "source_dataset_id":"dataset_id",
      "overwrite_destination_table":"true"
  }'

# Install Python packages from requirements.txt
pip install -r requirements.txt
