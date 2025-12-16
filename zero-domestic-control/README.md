# Zero Domestic Control

## Architecture

https://miro.com/app/board/uXjVI85VEAc=/?share_link_id=164545697008

### Development (Docker)

 - Install Hasura CLI: https://hasura.io/docs/2.0/hasura-cli/install-hasura-cli/
 - Create `.env` based on `.env-example` in the root folder. Make sure to set the `GCS_CREDENTIAL` to valid key.

Start services
```bash
docker compose --profile domestic up -d
```

Hasura metadata is applied at startup. To apply hasura metadata manually run:
```bash
cd ./volumes/hasura
hasura metadata apply --admin-secret myadminsecretkey
```

## Development

 - Install Hasura CLI: https://hasura.io/docs/2.0/hasura-cli/install-hasura-cli/
 - Create `.env` based on `.env-example` in the root folder. Make sure to set the `GCS_CREDENTIAL` to valid key.

Create environment
```bash
poetry install --with dev
```

Start services
```bash
docker compose --profile zero up -d
```

Run backend
```bash
poetry run python -m domestic_control api
```

Run stubs
```bash
poetry run python -m domestic_control stub
```

Run control
```bash
poetry run python -m domestic_control control
```

Apply hasura metadata
```bash
cd hasura
hasura metadata apply --admin-secret myadminsecretkey
```

### Generate JWT

Generate JWT
```bash
# With default 'user' role
poetry run python -m zero_domestic_control generate-jwt
# With additional role(s)
poetry run python -m zero_domestic_control generate-jwt admin
# With cabin (for guests)
poetry run python -m zero_domestic_control generate-jwt --cabin dutch-cabin
```

## Home Assistant

You can log into home assistant by running:

```bash
docker compose up hass
```

Go to http://localhost:8123 and log in with the following credentials:
Username: root
Password: zerozerozero
