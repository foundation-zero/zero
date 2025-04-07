# Zero Data
This repository contains the Zero data platform and the scripts to process the IO lists supplied by various parties into the SQL needed to process the values published by those parties.

# Release management

# zero-data

Tag a new release on Github. This will automatically deploy the tagged version to GAR.

# charts

The charts are deployed by their respective pipelines. Their versions are controlled by the `version` field in Chart.yaml.
The version of `zero-data` they deploy is based on the `appVersion`.

## Local Development
```bash
poetry install
```

# Local testing

```bash
docker compose up
```

This will setup
 - VerneMQ: MQTT Client
 - RisingWave: Streaming database
 - dbt_gen: DBT Model based on IO List
 - data_gen: MQTT signals based on IO list
