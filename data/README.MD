# Intro

This repo sets up the postgres and risingwave databases using pure SQL and `dbt`

# Setup

 - Create `.env` based on `.env.example`
 - Set up gsheet service account key file from Bitwarden

Install dependencies
```bash
poetry install
```

Start Postgres, Risingwave, VerneMQ and the data generator
```bash
docker compose up
```

Run the scripts for Postgres and Risingwave
```bash
poetry run python -m setup_postgres
poetry run python -m setup_risingwave
```
