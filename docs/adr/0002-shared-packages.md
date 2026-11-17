# Share domain logic in packages; copy plain infrastructure code

Apps share code through packages in `packages/`. Domain logic is always shared. Infrastructure code (logging, health checks, client setup) is copied into each app until it carries behaviour of its own.

## When to share

- **Domain logic: always share, however small.** Logic that encodes how the yacht or its systems work (yard tag normalisation, Modbus register decoding, unit conversions) lives in one package, even when it is five lines. When copies drift apart, two apps give different answers about the same equipment. A shared version is tested once, in one place.
- **Infrastructure code: copy by default.** Logging setup, a health endpoint, client configuration: when it is a few lines on top of a library, each app keeps its own copy. Saving a few lines is not a reason to share.
- **Share infrastructure code once it adds behaviour.** When the code holds logic that several apps would each have to get right, such as a workaround for a client library bug or a retry policy, it moves into a package. Fixing the library upstream comes first. A package for a temporary workaround is only worth it when several apps need it for a long time.

## Layout

- **Packages** live in `packages/py/<name>` and `packages/rust/<name>`. Apps stay in the repository root.
- **Path dependencies only.** Apps depend on a package by relative path: `<name> = { path = "../packages/py/<name>" }` under `[tool.uv.sources]` for uv, `<name> = { path = "../packages/rust/<name>" }` under `[dependencies]` for Cargo. Nothing is published to a registry, so an app always builds against the package source in the same commit.
- **Docker builds** use the repository root as context and copy or bind-mount `packages/py` or `packages/rust` into the build stage, so the path dependency resolves the same way as locally.
- **Existing shared code moves into `packages/`.** `zero-modbus-bridge`, which three apps already use as a path dependency from the root, moves to `packages/py` first.
- **Each package has one purpose** and holds code that changes together. No catch-all `common` or `utils` package.

## CI

- **Each package has its own workflow** that runs its tests and static checks when the package changes.
- **Every app that depends on a package also runs its CI when the package changes,** through the path filters of its workflow. The app installs the package from source, so its tests run against the changed package.
- **They run in parallel.** The app CI does not use anything the package CI produces, so there is nothing to wait for; both must pass before a PR merges.
- **A check catches missing path filters.** It reads the path dependencies of every app, including indirect ones, and fails when an app's workflow does not run on changes to one of them. Without it, a package change can skip the CI of an app that uses it, and nobody notices.

## Considered options

**Copy all shared code into each app.** Every app stays self-contained and CI only runs for the app that changed. We rejected it for domain logic: copies drift, and a fix in one app does not reach the others.

**One shared package for everything.** Simpler to set up, but it couples unrelated apps: every change to it runs CI for every app, and apps pull in dependencies they don't use.

**Publish packages to a registry with version numbers.** Apps could upgrade one at a time, but a fix needs a release and a bump in each app. With all apps in one repository, path dependencies plus CI on every dependent app catch a breaking change without that release step.

**Move apps into an `apps/` folder.** It would make the split between apps and packages visible, but it changes every app, chart, workflow and Dockerfile, and nothing else improves.
