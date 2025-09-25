# Setup

 - Create `.env` based on `.env-example`
 - `poetry install --with dev,test`
 - `docker compose up`
 - `cd hasura`
 - `hasura metadata apply --admin-secret adminsecretkey`


## Backend

Run Adapter
```bash
poetry run python -m backend adapter
```

Run stub
```bash
poetry run python -m backend stub
```

Run API
```bash
poetry run python -m backend api
```

Generate JWT token for a role
```bash
poetry run python -m backend generate-jwt --roles captain
```
