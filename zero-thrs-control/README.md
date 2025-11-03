# Zero THRS control

## FMU

Compile an FMU with FMPy by running:

```bash
poetry run fmpy compile <path-to-fmu-file>
```

Note: Setting CFLAGS prior is required to resolve mkdtemp function declaration conflicts in Dymola 2026 generated code when compiling on macOS.

```bash
export CFLAGS="-include unistd.h" poetry run fmpy compile <path-to-fmu-file>
```

## Simulator

Run the simulator with:

```bash
poetry run python -m thrs.cli run thrusters
```
Or 
```bash
poetry run python -m thrs.cli run pvt
```

The UI is in [zero-ui](../zero-ui) under [http://localhost:5173/thrs/hmi].

## Installation

Install the dependencies as (on MacOS):

```bash
brew install graphviz
export CFLAGS="-I $(brew --prefix graphviz)/include"
export LDFLAGS="-L $(brew --prefix graphviz)/lib"
poetry install
```

## GraphQL

### Running API

Run the API with

```bash
poetry run fastapi dev src/thrs/graphql/strawberry.py
```

### Export schema

Export the graphql schema to zero-ui with

```bash
poetry run strawberry export-schema thrs.graphql.strawberry --output ../zero-ui/src/graphql/thrs/schema.graphql
```
