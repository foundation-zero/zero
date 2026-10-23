set shell := ["bash", "-euo", "pipefail", "-c"]

# Generate the AsyncAPI specs of all services into ./specs
generate_specs:
    bash scripts/aggregate-specs.sh

# Same, but a failing service fails the recipe (as in CI)
generate_specs_strict:
    AGGREGATE_STRICT=1 bash scripts/aggregate-specs.sh

# Run a recipe across all subprojects, continuing on errors and reporting failures
run-all recipe:
    #!/usr/bin/env bash
    set -euo pipefail

    failed=()

    # Find all subdirectories containing a Justfile/justfile
    for dir in $(find . -mindepth 2 -maxdepth 2 \( -name "Justfile" -o -name "justfile" \) | xargs -n1 dirname | sort); do
        echo "========================================"
        echo "==> Running '{{ recipe }}' in $dir"
        echo "========================================"

        # Disable 'exit on error' so execution continues if 'just' fails
        set +e
        just "$dir/{{ recipe }}"
        status=$?
        set -e

        if [ $status -ne 0 ]; then
            failed+=("$dir")
        fi
        echo ""
    done

    # Print summary of results
    if [ ${#failed[@]} -gt 0 ]; then
        echo "❌ Command '{{ recipe }}' failed in the following project(s):"
        for f in "${failed[@]}"; do
            echo "   - $f"
        done
        exit 1
    else
        echo "✅ Command '{{ recipe }}' succeeded in all projects!"
    fi

lint:
    @just run-all lint

format:
    @just run-all format

test:
    @just run-all test

check:
    @just run-all check
