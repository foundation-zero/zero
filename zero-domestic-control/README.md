# Zero Domestic Control

## Development

Install Hasura CLI: https://hasura.io/docs/2.0/hasura-cli/install-hasura-cli/

Start external services
```bash
DOMESTIC_CONTROL_URL=http://host.docker.internal:8000/graphql docker compose up graphql-engine
```

Run database setup
```bash
poetry run python -m zero_domestic_control setup
```

Generate JWT
```bash
poetry run python -m zero_domestic_control generate-jwt
```

Run backend
```bash
poetry run fastapi dev zero_domestic_control/app.py
```

Run control
```bash
poetry run python -m zero_domestic_control setup
```

Run stubs
```bash
poetry run python -m zero_domestic_control stub
```

Apply hasura metadata
```bash
cd hasura
hasura metadata apply --admin-secret myadminsecretkey
```

### Without Python/poetry

Install Hasura CLI: https://hasura.io/docs/2.0/hasura-cli/install-hasura-cli/

Start services
```bash
docker compose up
```

Run database setup
```bash
docker compose up setup
```

Apply hasura metadata
```bash
cd volumes/hasura
hasura metadata apply --admin-secret myadminsecretkey
```

## Home Assistant

You can log into home assistant by running:

```bash
docker compose up hass
```

Go to http://localhost:8123 and log in with the following credentials:
Username: root
Password: zerozerozero
