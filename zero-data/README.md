# Zero Data
This repository contains the Zero data platform and the scripts to process the IO lists supplied by various parties into the SQL needed to process the values published by those parties.

# Release management

# zero-data

Tag a new release on Github. This will automatically deploy the tagged version to GAR.

# charts

The charts are deployed by their respective pipelines. Their versions are controlled by the `version` field in Chart.yaml.
The version of `zero-data` they deploy is based on the `appVersion`.

## Local Development

 - Install dependencies: `poetry install`
 - Create `.env` based on `.env.example`
    - Retrieve the `GCS_CREDENTIALS` from the cluster secret `gcs-auth`
    - Alternatively [Follow these instructions](https://docs.risingwave.com/integrations/destinations/google-cloud-storage) to create a service account key in Google Cloud and create the base64 encoded key

# Local testing (docker)

```bash
docker compose up
```

This will setup
 - VerneMQ: MQTT Client
 - RisingWave: Streaming database
 - dbt_gen: DBT Model based on IO List
 - data_gen: MQTT signals based on IO list

# Local testing

 - Install dependencies: `poetry install --with dev`
 - Create `.env` based on `.env.example`
    - Retrieve `GCS_CREDENTIALS` from `gcs-auth` secrets on the cluster or
    - [Follow these instructions](https://docs.risingwave.com/integrations/destinations/google-cloud-storage) to create a service account key in Google Cloud.
 - Generate DBT sql files: `poetry run zero-data generate-dbt`
 - Start data mocker: `poetry run zero-data generate-data`
