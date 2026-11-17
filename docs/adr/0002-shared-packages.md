# Share domain logic in packages; copy plain infrastructure code

Apps share code through packages in `packages/`. Domain logic is always shared. Infrastructure code (logging, health checks, client setup) is copied into each app until it carries behavior of its own.

## When to share

- **Domain logic: always share, however small.** Logic that encodes how the yacht or its systems work (yard tag normalization, Modbus register decoding, unit conversions) lives in one package, even when it is five lines.
- **Infrastructure code: copy by default.** Logging setup, a health endpoint, client configuration: when it is a few lines on top of a library, each app keeps its own copy. Saving a few lines is not a reason to share.
- **Share infrastructure code once it adds behavior.** When the code holds logic that several apps would each have to get right, such as a workaround for a client library bug or a retry policy, it moves into a package. Fixing the library upstream comes first. A package for a temporary workaround is only worth it when several apps need it for a long time.

## Layout

- **Packages** live in `packages/py/<name>`, `packages/rust/<name>` and `packages/ts/<name>`. Apps stay in the repository root.
- **Path dependencies only.** Apps depend on a package by relative path: `<name> = { path = "../packages/py/<name>" }` under `[tool.uv.sources]` for uv, `<name> = { path = "../packages/rust/<name>" }` under `[dependencies]` for Cargo, `"<name>": "link:../packages/ts/<name>"` in `package.json` for pnpm. Nothing is published to a registry, so an app always builds against the package source in the same commit.
- **Docker builds** use the repository root as context and copy or bind-mount the `packages/` folder they need into the build stage, so the path dependency resolves the same way as locally.
- **Each package has one purpose** and holds code that changes together. No catch-all `common` or `utils` package.

## CI

- **Each package has its own workflow** that runs its tests and static checks when the package changes.
- **Every app that depends on a package also runs its CI when the package changes,** through the path filters of its workflow.
- **They run in parallel.** The app CI does not use anything the package CI produces, so there is nothing to wait for; both must pass before a PR merges.

## Considered options

**Copy all shared code into each app.** Every app stays self-contained and CI only runs for the app that changed. We rejected it for domain logic: copies drift, and a fix in one app does not reach the others.

**One shared package for everything.** Simpler to set up, but it couples unrelated apps: every change to it runs CI for every app, and apps pull in dependencies they don't use.

**Publish packages to a registry with version numbers.** Apps could upgrade one at a time, but a fix needs a release and a bump in each app. With all apps in one repository, path dependencies plus CI on every dependent app catch a breaking change without that release step.

**Move apps into an `apps/` folder.** It would make the split between apps and packages visible, but it changes every app, chart, workflow and Dockerfile, and nothing else improves.
