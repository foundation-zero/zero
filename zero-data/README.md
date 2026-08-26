# Zero Data

This repository contains the Zero data platform and scripts to process IO lists supplied by various parties into the SQL needed to process the values published by those parties.

## Usage

1. Create a `.env` file based on `.env-example` in the root folder.

3. Start the services. Run in the root folder:
```bash
docker compose --profile data up -d
```

## Development Setup

1. Install dependencies:
   ```bash
   uv sync --locked
   ```

2. Create a `.env` file in the root folder based on `.env.example`.

3. Set up the GSheet service account key file from Bitwarden.

4. Start the required services. Run in the root folder:
   ```bash
   docker compose --profile zero up -d
   ```

5. Create a `.env` file in this folder based on `.env.example`.

### Running Components

Generate DBT SQL files:
```bash
uv run zero-data generate-dbt
```

Start the data mocker:
```bash
uv run zero-data generate-data
```

## Testing

1. Make sure the dependencies for testing are installed
   ```bash
   uv sync --locked
   ```
1. Run the tests
   ```bash
   uv run pytest .
   ```

## Release Management

### Charts

The charts are deployed by their respective pipelines. Their versions are controlled by the `version` field in `Chart.yaml`. The version of `zero-data` they deploy is based on the `appVersion`.

## Firedetection metadata

The `metadata` folder contains an SQL file for creating and filling a metadata table in Greptime DB used for firedetection data. This table is now created by hand until a method is found to automate this process.
