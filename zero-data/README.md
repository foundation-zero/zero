# Zero Data
This repository contains the Zero data platform and the scripts to process the IO lists supplied by various parties into the SQL needed to process the values published by those parties.

## Development
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
