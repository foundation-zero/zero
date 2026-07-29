# Zero Code Style

> Tooling configuration is the source of truth for mechanically enforced rules.
> Everything else here is convention. Follow it, or have a reason not to.

---

## 1. Quick Reference

### Python

```
Package:  snake_case, Poetry, poetry-dynamic-versioning
Types:    pydantic BaseModel/BaseSettings, 3.12+ generics (list[T] not List[T])
Async:    asyncio.TaskGroup, aiomqtt, @asynccontextmanager
Log:      %(asctime)s | %(levelname)-8s | %(message)s
Testing:  pytest + pytest-asyncio, asyncio_mode=auto, function loop scope
Idioms:   comprehensions > loops, f-strings, pathlib, MqttTopic not MQTTTopic
```

### TypeScript/Vue

```
Format:   100ch, double quotes, semicolons, trailing commas, single attr/line
Vue:      <script setup lang="ts"> → <template> → <style>
Stores:   Pinia setup-function syntax
Styles:   Tailwind utilities + cn() for merging
Testing:  Vitest, *.spec.ts (unit), *.integration.spec.ts (API), msw for mocks
Idioms:   arrow fns, const > let, ?./??, map/filter over for, backticks, as T
```

### Rust

```
Errors:   anyhow for applications, thiserror for libraries
Derives:  serde::Deserialize, Debug, Clone, clap::Parser
Async:    JoinSet, Arc<T>, log-and-continue on errors
Testing:  #[cfg(test)] inline modules, unwrap() only in tests
Log:      env_logger + log facade (info!/debug!/error!)
Config:   config crate (env vars) + dotenvy
Idioms:   match/if let, ? everywhere, /// docs on all public API
```

## 2. Python

### 2.1 Package Management

| Rule | Convention |
|------|------------|
| Build system | Poetry (all 7 Python projects). |
| Versioning | `poetry-dynamic-versioning` from git tags. All packages keep `0.0.0` in pyproject. |
| Python version | Each service specifies its own in `pyproject.toml`. Most require `>= 3.13.1,<4.0`; `zero-thrs-control` uses `<3.14`. |

### 2.2 Naming

Semantic names are preferred over generic names like "list" or "result".
```python
# Good
clothing = ["shirt", "trousers", "socks"]
# Bad
items = ["shirt", "trousers", "socks"]
```

It's preferable to lean on context to keep variable names short as long as it stays unambiguous.
```python
# Good
# in clothing.py
class Wardrobe:
  def hang(self, article: Article):
    self._rod_articles.append(article)

# Bad
# in clothing.py
class ClothingWardrobe:
  def hang_clothing_article(self, clothing_article: ClothingArticle):
    self._clothing_rod_articles.append(clothing_article)

# Good
shelf_articles = ["shirt"]
rod_articles = ["trousers"]
all_articles = shelf_articles + rod_articles

# Bad
articles = ["shirt"]
articles.append("trousers")
```

Do not introduce new abbreviations. Do not abbreviate if it introduces ambiguity.
```python
# Good
shelf_articles = ["shirt"]

# Bad
s_articles = ["shirt"]

# Good
delay_ms = 500 # ms is an established abbreviation

# Bad
stock_ms = 20 # Unclear between milliseconds and MicroSoft
```

- **Packages**: `snake_case` — `zero_termodinamica`, `domestic_control`, `zero_hull_temperature`.
- **Project names** (in `pyproject.toml`): vary. Some use the `zero-` prefix (`zero-termodinamica`),
  some omit it (`thrs`, `domestic-control`, `loads`, `generator`). Prefer the
  `zero-` prefix for new projects.
- **Modules**: `snake_case.py`.
- **Classes**: `PascalCase`.
- **Functions and methods**: `snake_case`.
- **Acronyms**: capitalize like regular words — `MqttTopic` not `MQTTTopic`, `PcanClient` not `PCANClient`.
- **MQTT / data fields**: JSON field names are lowercase and non-abbreviated.
  Topic segments are lower case, dasherized (kebab-case).

### 2.3 Type Annotations

- Use Python 3.12+ generics: `list[T]`, `dict[K, V]`, `tuple[X, Y]`.
  Avoid `typing.List`, `typing.Dict`, `typing.Tuple`.
- Pydantic `BaseModel` or `BaseSettings` is the standard data container.
  Avoid `dataclasses` in production code.
- Standard `SettingsConfigDict`:
  ```python
  model_config = SettingsConfigDict(
      env_file=".env",
      env_file_encoding="utf-8",
      extra="allow",
      env_nested_delimiter="__",
  )
  ```
- Use `Annotated` for Pydantic fields that need extra metadata.

### 2.4 Logging

The shared log format is:

```
%(asctime)s | %(levelname)-8s | %(message)s
```

- Use `logging.getLogger(__name__)` for per-module loggers, stored as `logger`:
  ```python
  import logging
  logger = logging.getLogger(__name__)
  ```
- Pytest config adds millisecond precision: `%(asctime)s.%(msecs)03d`.
- Pytest `log_level` is `DEBUG`.

### 2.5 Testing (pytest)

- **Markers**: `io`, `mqtt`, `slow`
- **Unit/integration split**: `tests/unit/` and `tests/integration/` where present

### 2.6 Dependency Groups

Poetry projects use three scopes:

| Scope | Purpose | Key packages |
|-------|---------|-------------|
| `dependencies` (top-level) | Runtime | aiomqtt, pydantic-settings, fastapi, strawberry-graphql |
| `[tool.poetry.group.dev]` | Development | ruff, mypy/pyright, python-dotenv, Jupyter |
| `[tool.poetry.group.test]` | Testing (optional) | pytest, pytest-asyncio, httpx, pytest-mock |

### 2.7 Idioms & Comment Style

**Comprehensions:** Prefer comprehensions over `map`/`filter`. If a comprehension
gets unwieldy, split into intermediate variables rather than falling back to a
stateful loop.

```python
[controller.enabled() for controller in self._valve_controllers]
{name: getattr(module, name) for name in names}

# If complex, split:
base = {name: getattr(module, name) for name in names}
extra = {k: v for k, v in computed.items() if v is not None}
merged = base | extra
```

- `any()` / `all()` / `sum()` take generator expressions.
- A comprehension signals a result is being built. Pure side effects can use a loop.

**Tuple destructuring:** `a, b = result` rather than `result[0]`, `result[1]`.

**Context managers:** `async with` is the standard. `@asynccontextmanager` for
resource factories. Use `contextmanager` to hide setup/teardown at call sites.

**Pattern matching (`match`/`case`):** Use where it improves readability over
`if`/`elif` chains.
- Use `assert_never()` for exhaustiveness checking in match statements.

**Walrus operator (`:=`):** Use sparingly in conditionals:
`if (result := self.result()) and condition(result):`.

**String formatting:** f-strings. Avoid `str.format()` and `%`-formatting.

**Concurrent tasks**:
- Use `asyncio.TaskGroup` for structured concurrency. Avoid `asyncio.gather`.

**Path handling:** `pathlib.Path` over `os.path`.

**Enums:** `enum.Enum` or `StrEnum` for finite value sets.

**Private fields:** Avoid accessing `_prefixed` attributes from outside the class.
Use `@property` or a named getter.

**Functional boundaries:** Prefer callables over dict-lookup dispatch.

**`print`:** For CLI output. Use `logging.getLogger(__name__)` for runtime messages.

**Comments:**

- Comments explain *why*, not *what*.
- Skip comments that restate the code — a reader knows what `apt-get install` does.
- If a comment raises more questions than it answers, rewrite or remove it.
- `# TODO:` is the convention for deferred work. Other markers (`FIXME`, `HACK`,
  `XXX`) are not used.

**Tests:**

- Use `nullcontext` from `contextlib` to make "does not raise" explicit in parametrized tests.

---

## 3. TypeScript & Vue (`zero-ui/`)

### 3.1 Path Aliases

| Alias | Resolves to |
|-------|------------|
| `@/` | `src/` |
| `@env` | `src/settings/index.ts` |
| `@common/*` | `src/modules/common/*` |
| `@tests/*` | `tests/*` |
| `@components/*` | `src/components/ui/*` |
| `@modules/*` | `src/modules/*` |

> The root `tsconfig.json` and `vitest.config.ts` define `@modules/*` as
> `src/components/modules/` and `@env` as a directory. The aliases above are
> the intended targets; these inconsistencies should be resolved.

### 3.2 Vue SFC Structure

Every `.vue` file follows this order:

1. `<script setup lang="ts">`
2. `<template>`
3. `<style>` (rare; Tailwind handles styling)

```vue
<script setup lang="ts">
import { computed } from "vue";
import { cn } from "@common/lib/utils";

const props = defineProps<{ class?: string }>();
</script>

<template>
  <div :class="cn('flex flex-col gap-4', props.class)">
    <slot />
  </div>
</template>
```

- Components are `PascalCase`, multi-word, in a directory with `index.ts` barrel export.
- `defineProps` uses the type-only generic syntax: `defineProps<{ ... }>()`.
- Use `cn()` from `@common/lib/utils` when a component accepts a `class` prop.

### 3.3 Module Organization

Feature modules live under `src/modules/<name>/`:

```
modules/<name>/
  router/          # Route records, guards
  stores/          # Pinia stores
  views/           # Page-level SFCs
  components/      # Module-local components
  graphql/         # urql client, queries, schema
  types/           # Module-level types
  lib/             # Constants, helpers
  layouts/         # Layout components
  mimics/          # Mimic diagram providers (thrapp only)
  tests/           # Integration tests
```

Shared code in `modules/common/`:

- `lib/utils.ts` — `cn()`, `useDemoValues`, `useSafeRange`, `useAutoFocus`.
- `types/index.ts` — `Stamped<T>`, `ChartDataType`, `TimeSeriesData`.

### 3.4 Pinia Stores

Use setup-function syntax.

```ts
export const useAutomationStore = defineStore("automation", () => {
  const active = ref(false);
  return { active };
});
```

Name store files after their domain: `stores/thrs.ts`, `stores/auth.ts`.

### 3.5 GraphQL (urql)

- Each module has its own urql `Client` in `graphql/client.ts`.
- Queries and mutations are raw template strings:
  ```ts
  const MUTATE_CONTROL = gql`
    mutation setControlValue($input: SetControlInput!) {
      setControl(input: $input) { success }
    }
  `;
  ```
- Subscriptions use `graphql-ws` transport.

### 3.6 Routing

- The root router (`src/router.ts`) aggregates routes from each enabled module.
- `VITE_INCLUDE_APPS` gates which modules are active.
- Load layouts dynamically: `<component :is="$route.meta.layout" />`.
- Use async `() => import(...)` for views and layouts.

### 3.7 Testing (Vitest)

| Suite | Convention |
|-------|------------|
| Unit | `*.spec.ts`, co-located with source. Mock with `msw` and `@pinia/testing`. |
| API integration | `**/api.integration.spec.ts` in `tests/`. Use real `urql` clients. |

Config: `globals: true`, `environment: "jsdom"`, `clearMocks: true`.

### 3.8 Idioms & Comment Style

- **Arrow functions** as the default. Function declarations for exported utilities.
- **`const`** is the default. `let` for mutable closed-over state.
- **Optional chaining + nullish coalescing** together:
  `props.thresholds?.toSorted((a, b) => a - b) ?? []`.
- **Array methods** (`map`/`filter`/`reduce`/`some`/`every`) over raw `for` loops.
  `for` loops are fine when iteration needs complex control flow.
- **Template literals** (backticks) for string interpolation. Avoid `+` concatenation.
- **Type assertions**: `as T`. Avoid angle-bracket `<T>`.
- **Enums**: Prefer `const object` or `as const` array with derived union types.
  GraphQL codegen output is the exception — generated `enum` is fine.
- **Destructuring**: Object destructuring is universal. Array destructuring is occasional.
- **`async`/`await`** for async operations. Avoid `.then()` chains.
- **Lodash** utilities are available: `minBy`, `maxBy`, `sumBy`, `groupBy`.
- **`useTemplateRef`** is the preferred Vue 3 way to reference DOM elements.
- **Extract reusable types** — `ActualAndSetpoint<T>` rather than repeatedly
  inlining `actualX | xSetpoint`.

**Comments:**

- `//` comments explain *why*, not *what*.
- `/** JSDoc */` is used in generated code and for component descriptions.
- `TODO` is the only marker convention. Avoid `FIXME`, `HACK`, `XXX`, `OPTIMIZE`.

---

## 4. Rust (`zero-fiber-optics/`)

### 4.1 Crate Setup

- Binary crate. Flat module structure (`src/*.rs`). Declare modules with
  `mod name;` in `main.rs`.

### 4.2 Error Handling

- **anyhow** for application-level errors. Functions return `anyhow::Result<T>`.
- `.context()` / `.with_context()` for error enrichment.
- `bail!()` for early validation failures.
- `nom::IResult` in parser code, converted to `String` at the adapter boundary.
- `thiserror` is for libraries; the monorepo uses `anyhow` for applications.

### 4.3 Derive Macros

- `serde::Deserialize` on all config types, with `#[serde(rename_all = "camelCase")]`.
- `clap::Parser` + `clap::Subcommand` on CLI structs.
- `Debug, Clone` on all data structs.

### 4.4 Async (tokio)

- `#[tokio::main]` entry point (multi-threaded runtime).
- `tokio::task::JoinSet` to manage spawned handles — drain with `join_next()`.
- `Arc<T>` for shared state across tasks.
- Error recovery: log and continue on non-fatal errors; sleep 500ms on UDP recv error.

### 4.5 Testing

- **Inline `#[cfg(test)] mod tests`** in every file with business logic.
- Helper constructors at test-module level to reduce boilerplate.
- `#[should_panic]` for expected panics.
- Literal byte arrays for parser test input.

### 4.6 Logging

- `env_logger::init()` at startup, after `dotenvy::dotenv().ok()`.
- `log` facade: `info!`, `debug!`, `error!`. No structured logging.

### 4.7 Configuration

- Application config: `config` crate with environment variable source.
  Defaults: `mqtt_host=localhost`, `mqtt_port=1883`, `mqtt_prefix=telemetry`.
- `.env` files supported via `dotenvy`.
### 4.8 Naming

- Standard Rust: `snake_case` for functions/variables, `CamelCase` for types.

### 4.9 Idioms & Comment Style

- **`match`** for exhaustive discrimination (parser dispatch, CLI commands, errors).
- **`if let`** for single-pattern matches (error-only branches, optional destructuring).
- **`while let`** for stream consumption and JoinSet draining.
- **`let`-`else`** for early returns on missing required values (rare).
- **Iterator chains** (`.map()`/`.filter()`/`.collect()`) and `for` loops are both
  standard. `try_fold` for fallible accumulation.
- **`?` operator** is ubiquitous. Couple with `.context()` for error enrichment.
- **`unwrap()`** only in `#[cfg(test)]`. Production code uses `unwrap_or()`,
  `unwrap_or_else()`, or `?`.

**Comments:**

- `///` doc comments on every public function, struct, and enum.
  Private functions can skip doc comments.
- `//` line comments are sparse — use for non-obvious logic.
- No `//!` module-level doc comments.
- No `TODO`, `FIXME`, or `HACK`. No `/* ... */` block comments.

---

## 5. Cross-Cutting Infrastructure

### 5.1 Docker

Every service has a `Dockerfile` in its project directory.

**Service profiles** (`docker-compose.yml`):

| Profile | Services |
|---------|----------|
| `zero` | vernemq, postgres, hasura, hass |
| `data` | data-gen, dbt-gen, grafana |
| `data-collection` | vector, greptimedb |
| `domestic` | domestic-control-api, domestic-control-control, domestic-control-stub |
| `loads` | loads-api, loads-at-sensors-stub, loads-fiber-optic-sensors-stub, loads-sail-system-sensors-stub |
| `loads-dev` | loads-conditions-stub |
| `thrs` | thrs-api, thrs-control-thrusters |
| `thrs-extra` | thrs-control-{high_temperature,pvt,pcm,consumers,dhw} |

> `hasura` and `hass` are also in the `domestic` profile.

- Every chart needs a `values.schema.json` for validation.
- Every file ends with a newline.
- Default to production values; override per-environment in deployment config.
- Strip boilerplate comments from `values.yaml`, `Chart.yaml`, and CI workflow files.

### 5.2 Task Runner (just)

`just` for development commands. Standard recipe pattern:

```just
check: lint type_check test
lint:
    poetry run ruff check
type_check:
    poetry run pyright
test *args:
    poetry run pytest {{ args }}
```

### 5.3 Environment Variables

- Root `.env.example` defines shared variables: `PG_USER`, `PG_PASSWORD`, `PG_DB`,
  `JWT_SECRET`, `HOME_ASSISTANT_TOKEN`.
- Each service may have its own `.env.example`.
- Vite loads `VITE_*` prefixed variables.
- Python loads via `pydantic-settings` with `env_file=".env"`.

### 5.4 CI (GitHub Actions)

**Triggers:** `pull_request` + `push` to `main` (path-filtered per project) +
`release` (type `released`).

**Standard pipeline:**

```
test (lint → type-check → unit test → integration test)
  → docker-push (GCP Workload Identity → Artifact Registry)
```

| Language | Pipeline |
|----------|----------|
| Python | `poetry install --with dev,test` → `ruff check` + `ruff format --check` → `pyright`/`mypy` → `pytest` (unit, then integration against `docker compose` services) |
| Rust | `setup-rust-toolchain` (clippy, rustfmt) → `cargo test --locked` → `cargo clippy --locked` |
| TypeScript | `pnpm install` → `pnpm lint --max-warnings 0` → `pnpm test:unit` → `docker compose` services → `pnpm test:api` → `pnpm exec playwright test` → Cloudflare Pages deploy |

**Docker tagging:** Python projects use `poetry version -s` (via `poetry-dynamic-versioning`
from git tags). Rust uses `Cargo.toml` version + short SHA. CI apps use
`docker/metadata-action` (semver + sha).

**Helm charts:** Workflows delegate to the reusable `job_helm_push.yaml`.
Charts are pushed as OCI artifacts to GCP Artifact Registry.

**Artifact registry:** `europe-west1-docker.pkg.dev/common-449414/common/<image>`.
Multi-arch (`linux/amd64,linux/arm64`) for services, single-arch for frontend/infra.

### 5.5 Editor Integration

- `.vscode/settings.json` configures pytest for `zero-loads-app`.
- No repo-level `.editorconfig`. Configure tooling via editor extensions.

