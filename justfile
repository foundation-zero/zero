set shell := ["bash", "-euo", "pipefail", "-c"]

# Generate the AsyncAPI specs of all services into ./specs
generate_specs:
    bash scripts/aggregate-specs.sh

# Same, but a failing service fails the recipe (as in CI)
generate_specs_strict:
    AGGREGATE_STRICT=1 bash scripts/aggregate-specs.sh
