# Shared Python packages

Code that more than one service in this repo uses. The packages are not
published: a service depends on one by path, so a change here reaches every
service that uses it in the same PR.

```toml
[project]
dependencies = ["zero-health"]

[tool.uv.sources]
zero-health = { path = "../packages/py/zero-health" }
```

A service that depends on a package also copies it into its Docker build and
adds `packages/py/<package>/**` to the path filters of its CI workflow, so a
change to the package rebuilds and retests the service.

Each package has its own `pyproject.toml`, `uv.lock`, `justfile` and CI
workflow (`.github/workflows/ci_<package>.yaml`); there is no uv workspace.

- [zero-health](zero-health): readiness and liveness endpoints.
