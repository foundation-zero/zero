**Overview**
- Settings are resolved in [settings/index.ts](settings/index.ts) and exposed through `env.get()`.
- Development (and tests) read from `import.meta.env`, which is populated by Vite from `.env*` files.
- Production reads a JSON file at runtime so Docker can swap configuration without rebuilding.

**Development**
- Vite loads `.env`, `.env.local`, and mode-specific files (for example `.env.test`) and exposes `VITE_*` variables on `import.meta.env`.
- When `import.meta.env.MODE === "development"` or `import.meta.env.VITEST` is true, settings are read directly from `import.meta.env`.
- Keep non-`VITE_` variables out of client code; only `VITE_` prefixed keys are exposed.

**Production (Docker)**
- On startup in production mode, the app fetches `/env.json` and uses its values as the settings source.
- The JSON file must be present in the web root (see [public/env.json](public/env.json) for the template).
- In Docker, replace or mount `env.json` in the container so the frontend picks up environment-specific values without rebuilding.
- The JSON should contain all keys from [settings/keys.ts](settings/keys.ts) as strings.

**Notes**
- The runtime fetch is performed with `cache: "no-store"` so changes to `env.json` are picked up on reload.
- If the JSON file cannot be loaded, the app throws to avoid running with undefined settings.
