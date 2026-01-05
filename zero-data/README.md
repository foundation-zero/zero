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
   poetry install --with dev
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
poetry run zero-data generate-dbt
```

Start the data mocker:
```bash
poetry run zero-data generate-data
```

## Testing

1. Make sure the dependencies for testing are installed
   ```bash
   poetry install --with dev,test
   ```
1. Run the tests
   ```bash
   poetry run pytest .
   ```

## Release Management

### Charts

The charts are deployed by their respective pipelines. Their versions are controlled by the `version` field in `Chart.yaml`. The version of `zero-data` they deploy is based on the `appVersion`.
