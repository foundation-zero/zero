# Zero Domestic Control

## Architecture

Refer to the architecture diagram: [Miro Board](https://miro.com/app/board/uXjVI85VEAc=/?share_link_id=164545697008)

## Usage

1. Install the Hasura CLI: [Hasura CLI Installation Guide](https://hasura.io/docs/2.0/hasura-cli/install-hasura-cli/)

2. Create a `.env` file based on `.env-example` in the root folder.

3. Start the services. Run in the root folder:
    ```bash
    docker compose --profile domestic up -d
    ```

### To manually apply Hasura metadata:

```
cd hasura
hasura metadata apply --admin-secret myadminsecretkey
```

## Development Setup

1. Install dependencies:
    ```bash
    uv sync --locked
    ```

2. Create a `.env` file in the root folder based on `.env-example`.

3. Start the required services. Run in the root folder:
    ```bash
    docker compose --profile zero up -d
    ```

4. Create a `.env` file in this folder based on `.env-example`.

### Running Components

Run the backend:
```bash
uv run domestic_control api --reload true
```

Run the stubs:
```bash
uv run domestic_control stub
```

Run the control process:
```bash
uv run domestic_control control
```

### Generate JWT

Generate a JWT token:
```bash
# Admin role
uv run domestic_control generate-jwt --roles admin
# Cabin-specific token
uv run domestic_control generate-jwt --cabin dutch-cabin
```

## Testing

1. Make sure the dependencies for testing are installed
```bash
uv sync --locked
```
2. Run unit tests
```bash
uv run pytest --run=unit
```
3. Run integration tests:

Start the required services. Run in the root folder:
```bash
docker compose --profile zero up -d
```

Run the integration tests:
```bash
uv run pytest --run=integration
```
