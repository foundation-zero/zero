# Setup

 - Create `.env` based on `.env-example`
 - `poetry install --with dev,test`
 - `docker compose up`
 - `cd hasura`
 - `hasura metadata apply --admin-secret adminsecretkey`


## loads

Run Adapter
```bash
poetry run python -m loads adapter
```

Run stub
```bash
poetry run python -m loads stub
```

Run API
```bash
poetry run python -m loads api
```

Generate JWT token for a role
```bash
poetry run python -m loads generate-jwt --roles captain
```
