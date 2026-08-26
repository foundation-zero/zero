# Mimic Content Workflow — Maintenance Instructions

**Audience: an AI agent (or developer) keeping the mimic sheet pipeline in sync.** When the
schema, the code, or the committed mimic data changes, apply the matching recipe below.

User-facing usage is documented in [README.md](./README.md); instructions for implementing a
filled plan are in [EXTENDING.md](./EXTENDING.md). Do not duplicate them here.

## Architecture

```
schema.graphql ──┐
committed dhw/   ┤ scripts/mimics/generate-sheet-tabs.ts ──► scripts/mimics/mimic-out/*.csv
thrusters data  ┘
filled plan CSV ──► scripts/mimics/verify-plan.ts ──► validation (--check: diff vs committed data)
```

| Entry point | Purpose |
|-------------|---------|
| `pnpm generate-sheet-tabs` | Rebuilds the CSVs in `scripts/mimics/mimic-out/`. |
| `pnpm verify-plan <plan.csv> [controllers.csv]` | Validates a filled plan export. |
| `pnpm verify-plan --check <plan.csv>` | Additionally diffs the plan against committed mimic data (replaces the old round-trip test). |

Shared library in `scripts/mimics/lib/`:

- `schema.ts` — parses `schema.graphql` into the datapoint catalog (`SchemaRow[]`).
- `data-parser.ts` — reads committed `data/**` back into canonical `InstanceModel`s (TS compiler
  API; handles `shared.ts` refs, spreads, factory folders, alias imports, getters, PID controllers).
- `templates.ts` — **canonical slot table** (`CANONICAL_SLOTS`) per component type, plus
  designer-facing type labels. The single place defining which slots exist per type.
- `sheet-tabs.ts` — serialises instances/controllers into the CSV formats.
- `csv.ts`, `enums.ts` — helpers (CSV I/O; schema-type ↔ enum-expression maps).

There is no code generator anymore; implementation of filled plans is done by hand/AI per
[EXTENDING.md](./EXTENDING.md). The invariants to protect are:

1. `plan-seed.csv` regenerated from committed dhw/thrusters must validate and `--check` clean:
   ```bash
   pnpm generate-sheet-tabs
   pnpm verify-plan --check scripts/mimics/mimic-out/plan-seed.csv scripts/mimics/mimic-out/controllers-seed.csv
   ```
2. Every slot used by committed code must exist in `CANONICAL_SLOTS` — otherwise the plan rows
   appear as unknown-slot errors during validation.

## Recipes

### Schema changed (new/renamed/removed datapoints)

1. Refresh the GraphQL schema if needed (`pnpm extract-all-schemas`, see `../README.md`).
2. `pnpm generate-sheet-tabs`; re-import `schema-catalog.csv` into the Schema tab.
3. Run the invariant check above; fix any newly-unresolvable references.

### Committed dhw/thrusters mimic data edited by hand

Run the invariant check. If it fails, either the hand edit introduced content not derivable
from the canonical slots (extend `CANONICAL_SLOTS` if legitimate), or the seed no longer matches
the sheet — re-import `instances.csv` / `controllers-seed.csv` / `plan-seed.csv`.

### New component type added in UI code

1. Ensure the UI component and its entries in `src/modules/thrapp/types/fields.ts` exist.
2. Add the type to `CANONICAL_SLOTS` and `TYPE_LABELS` in `lib/templates.ts`.
3. Verify with the invariant check after at least one instance exists.

### Slot added/changed on an existing type (design change)

1. Update `src/modules/thrapp/types/fields.ts`.
2. Mirror the change in `CANONICAL_SLOTS` (`lib/templates.ts`) — same slotId, valueKind, field
   types, required flag.
3. Regenerate tabs, re-import Templates into the sheet; run the invariant check.

### Whole new module added (e.g. `pcm`, `pvt`, `adsorption`)

1. Check the module's datapoints exist in `schema-catalog.csv` (`MIMIC_MODULES` in
   `lib/schema.ts` lists parsed modules).
2. Add the module to `SEED_MODULES` in `generate-sheet-tabs.ts` only if committed mimic data
   exists for it.
3. App wiring (mimic `.vue` page, `layers/`, registration in
   `src/modules/thrapp/views/Mimic.vue`) is NOT part of this workflow.

### Parser changed

The parser feeds both seeding and `--check`. After any change run the invariant check — it must
stay green for dhw/thrusters.

## Gotchas

- Plan values reference schema fields by their GraphQL name (`field` column C of the Schema
  tab), not by technicalName. Cross-module references are written `module:field`; the seeder
  qualifies automatically whenever a field name is ambiguous across modules.
- `controllerState.controller` accepts two forms: a raw `pidController` datapoint or
  `@controller:<name>`. Both are valid in plans and code.
- Factory folders (e.g. thrusters manual valves) generate instances without individual titles;
  missing `srcTitle` there is a warning, not an error.
- Path constants in the entry scripts are relative to their own location (`../../src/...`,
  `mimic-out`), so moving files requires updating those paths.
