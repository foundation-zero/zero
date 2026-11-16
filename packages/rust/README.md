# Shared Rust crates

Code that more than one service in this repo uses. The crates are not
published (`publish = false`): a service depends on one by path, so a change
here reaches every service that uses it in the same PR.

```toml
[dependencies]
zero-readiness = { path = "../packages/rust/zero-readiness" }
```

A service that depends on a crate also copies it into its Docker build (the
build context is the repository root) and adds `packages/rust/<crate>/**` to
the path filters of its CI workflow, so a change to the crate rebuilds and
retests the service.

Each crate has its own `Cargo.toml`, `Cargo.lock`, `rust-toolchain.toml`,
`justfile` and CI workflow (`.github/workflows/ci_<crate>.yaml`); there is no
Cargo workspace.

- [zero-readiness](zero-readiness): a readiness status file for an exec probe,
  and the not-ready deadline of ADR 0001.
