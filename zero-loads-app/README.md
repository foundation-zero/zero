# Setup

- `poetry install --with dev,test`
- `docker compose up`
- `cd hasura`
- `hasura metadata apply --admin-secret adminsecretkey`


# Introduction

This repository configures a PCanAdapter to listen on a specified IP address and port for UDP-wrapped PCan messages. It also includes a stub that periodically sends PCan messages to the same address.

# Setup

 - Create `.env` based on `.env-example`
 - `poetry install --with dev,test`


## Adapter
 - `poetry run python -m adapter adapter`
 - `poetry run python -m adapter stub`


# Api

Run API
```bash
poetry run python -m api api
```

Generate JWT token for a role
```bash
poetry run python -m api generate-jwt --roles captain
```
