# Data

This repository sets up the PostgreSQL and RisingWave databases using SQL and `dbt`.

## Setup Instructions

 - Create a `.env` file based on `.env.example`.
 - Set up the Google Sheets service account key file (`.gsheet-sa-key`) from Bitwarden.

Install dependencies:
```bash
poetry install
```

Start services (from the root folder):
```bash
docker compose --profile zero up
```

This will set up the following relevant services:
 - VerneMQ: MQTT client
 - RisingWave: Streaming database

Run the scripts for PostgreSQL and RisingWave:
```bash
poetry run python -m setup_postgres
poetry run python -m setup_risingwave
```
