# Setup

 - Create `.env` based on `.env-example`
 - `poetry install --with dev,test`
 - `docker compose up`
 - `cd hasura`
 - `hasura metadata apply --admin-secret adminsecretkey`


## Adapter

Run Adapter
```bash
poetry run python -m adapter adapter
```

Run stub
```bash
poetry run python -m adapter stub
```


# Api

Run API
```bash
poetry run python -m api api
```

Generate JWT token for a role
```bash
poetry run python -m api generate-jwt --roles captain
```
