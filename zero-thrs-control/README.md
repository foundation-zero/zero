# Zero THRS Control

## Development

Copy .env.example to .env and modify if appropriate:

```bash
cp .env.example .env
```

Install dependencies:

```bash
uv sync --locked
```

## FMU

To compile an FMU with FMPy, run:

```bash
just compile_fmu src/thrs/simulation/models/Thruster_Module_V19.fmu
```

Replace the FMU path with the file you want to compile.

The recipe sets `CFLAGS="-std=gnu17 -include unistd.h"` automatically.

On macOS, install graphviz first:

```bash
brew install graphviz
```

## Lockstep

Run the lockstep with:

```bash
just run_lockstep module=dhw
```
Replace `dhw` with one of: `thrusters`, `pvt`, `pcm`, `consumers`, `high_temperature` or `dhw`.

## Control

Run the control with:

```bash
just run_control module=dhw
```
Replace `dhw` with one of: `thrusters`, `pvt`, `pcm`, `consumers`, `high_temperature` or `dhw`.

## Simulator

Run the simulator with:

```bash
just run_simulation module=dhw
```

Replace `dhw` with one of: `thrusters`, `pvt`, `pcm`, `consumers`, `high_temperature` or `dhw`.

The UI is located in [zero-ui](../zero-ui) at [http://localhost:5173/thrs/hmi](http://localhost:5173/thrs/hmi).

## Installation

Install dependencies on macOS:

```bash
brew install graphviz
export CFLAGS="-I $(brew --prefix graphviz)/include"
export LDFLAGS="-L $(brew --prefix graphviz)/lib"
uv sync --locked
```

## GraphQL

### Running the API

Start the API with:

```bash
just run_api
```

### Exporting the Schema

Export the GraphQL schema to `zero-ui`:

```bash
just export_schema
```
