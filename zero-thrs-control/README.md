# Zero THRS Control

## FMU

To compile an FMU with FMPy, run:

```bash
poetry run fmpy compile <path-to-fmu-file>
```

**Note:** On macOS, set `CFLAGS` beforehand to resolve `mkdtemp` function declaration conflicts in Dymola 2026-generated code:

```bash
export CFLAGS="-include unistd.h"
poetry run fmpy compile <path-to-fmu-file>
```

## Simulator

Run the simulator with:

```bash
poetry run python -m thrs.cli run <module>
```

Where `<module>` can be one of: `thrusters`, `pvt`, `pcm`, `consumers`, `high_temperature` or `boilers`.

The UI is located in [zero-ui](../zero-ui) at [http://localhost:5173/thrs/hmi](http://localhost:5173/thrs/hmi).

## Installation

Install dependencies on macOS:

```bash
brew install graphviz
export CFLAGS="-I $(brew --prefix graphviz)/include"
export LDFLAGS="-L $(brew --prefix graphviz)/lib"
poetry install
```

## GraphQL

### Running the API

Start the API with:

```bash
poetry run fastapi dev src/thrs/graphql/strawberry.py
```

### Exporting the Schema

Export the GraphQL schema to `zero-ui`:

```bash
poetry run strawberry export-schema thrs.graphql.strawberry --output ../zero-ui/src/modules/thrs/graphql/schema.graphql
```
