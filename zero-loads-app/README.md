# Setup

 - Create `.env` based on `.env-example`
 - `poetry install --with dev,test`
 - `docker compose up`
 - `cd hasura`
 - `hasura metadata apply --admin-secret adminsecretkey`


## loads

Run Adapter
```bash
poetry run loads adapter
```

Run stub
```bash
poetry run loads stub
```

Run API
```bash
poetry run loads api
```

Generate JWT token for a role
```bash
poetry run loads generate-jwt --roles captain
```
