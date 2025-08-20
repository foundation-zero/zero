# Zero Domestic Control

## Architecture

https://miro.com/app/board/uXjVI85VEAc=/?share_link_id=164545697008

### Development (Docker)

Install Hasura CLI: https://hasura.io/docs/2.0/hasura-cli/install-hasura-cli/

Start databases and MQTT brokerpoet
```bash
docker compose up postgres risingwave vernemq -d
```

Run postgres and risingwave setup
```bash
cd ../data
poetry run python -m setup_postgres
poetry run python -m setup_risingwave
```

Run everything else. Control and stub
```bash
cd ../zero-domestic-control
docker compose up -d
```

Apply hasura metadata
```bash
cd ./volumes/hasura
hasura metadata apply --admin-secret myadminsecretkey
```


## Development

Install Hasura CLI: https://hasura.io/docs/2.0/hasura-cli/install-hasura-cli/

Create environment
```bash
poetry install
```

Start databases
```bash
docker compose up postgres risingwave -d
```

Run Postgres database setup
```bash
docker compose up setup_postgres
```

Run dbt database setup
```bash
cd data/risingwave
poetry run python -m run_dbt.py
```

Run Risingwave database setup
```bash
docker compose up setup_risingwave
```

Run backend
```bash
poetry run fastapi dev zero_domestic_control/app.py
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
