# Shared Python packages

Code that more than one service in this repo uses. The packages are not
published: a service depends on one by path, so a change here reaches every
service that uses it in the same PR.

```toml
[tool.uv.sources]
zero-modbus-bridge = { path = "../packages/py/zero-modbus-bridge", editable = true }
```

A service that depends on a package bind-mounts `packages/py` into the
`uv sync` step of its Docker build (the build context is the repository root)
and adds `packages/py/<package>/**` to the path filters of its CI workflow, so
a change to the package rebuilds and retests the service.

Each package has its own `pyproject.toml`, `uv.lock`, `justfile` and CI
workflow in `.github/workflows`; there is no uv workspace.

- [zero-modbus-bridge](zero-modbus-bridge): Modbus-TCP to MQTT bridge with
  AsyncAPI generation.
