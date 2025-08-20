# Zero THRS control

## Simulator

Run the simulator with:

```bash
poetry run python -m cli run thrusters
```

The UI is in [zero-ui](https://github.com/foundation-zero/zero-ui) under [http://localhost:5173/thrs].

## Installation

Install the dependencies as (on MacOS):

```bash
brew install graphviz
export CFLAGS="-I $(brew --prefix graphviz)/include"
export LDFLAGS="-L $(brew --prefix graphviz)/lib"
poetry install
```
