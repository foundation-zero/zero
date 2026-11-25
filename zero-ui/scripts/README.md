# Scripts

Node.js scripts that generate or convert zero-ui's code and data.

## Scripts

### `generate-tooltips.ts`

Generates `src/modules/thrapp/mimics/data/tooltips.json` from every
`src/modules/thrapp/mimics/data/*/index.ts` module aggregate.

```bash
pnpm generate-tooltips
pnpm generate-tooltips --check
```

The output contains each complete tooltip context, including sources, sensors,
controls, parameters, controller state, custom data, and evaluated `tooltip`
getters. Nested getters are evaluated too. The original TypeScript data is not
changed, and switching application consumers to JSON is a separate step.

The JSON has two root objects: `register` and `contexts`. Contexts are grouped
by `MimicComponentType`, with unprefixed `YardTagOrModuleField` keys inside each
group, for example, `contexts.CheckValve["1188-03"]`. Register values retain the
component-type prefix. Tagged tooltips have two registry aliases, using the
instance key and `module:instance`: both `"1188-03"` and `"pvt:1188-03"` map to
`"CheckValve/1188-03"`. Tooltips without a yard tag only have the qualified
alias, for example, `"dc:aft": "DcConverter/dc:aft"`. Inferred numeric yard tags
also get both aliases. Component types sharing a tag keep separate entries in
their respective groups; each registry alias points to its first match in module
and instance iteration order.

Tag selection uses the resolved tooltip's `yardTag`, then a numeric instance
key, otherwise `module:instance`. Inferred tags are also added to the generated
tooltip content. If the selected tag is empty, the key falls back to
`module/field`.
Structurally identical contexts under the same typed key are deduplicated,
regardless of object property order. A key with one distinct context holds a
single object; a key with multiple distinct contexts holds an array, preserving
first-occurrence order. Contexts with different data are retained.

The script uses Vite to build a temporary Node bundle, replacing Vue component
imports with inert exports while evaluating the real data helpers. No browser,
running dev server, or backend is required. Temporary files are cleaned up even
on failure. `--check` verifies that the checked-in JSON matches the source data
without writing it.

### `generate-mqtt-graphql-queries.ts`

Generates thrapp's definitions (`src/modules/thrapp/lib/definitions.generated.ts`) and its
MQTT GraphQL fragments (`mqtt-graphql-queries.generated.ts`) from the AsyncAPI Specs, the
marpower Spec from zero-data and the thrs-control Spec. It regenerates the Specs first
(`just generate_specs`), unless `--skip-specs` is given.

```bash
just generate_mqtt_graphql_queries
pnpm generate-mqtt-graphql-queries --skip-specs
```

Components are identified by their technical name and grouped by zero-data's modules. What the
Specs don't say yet is a placeholder in the script: a valve's type, from its technical name,
and the parameters' kinds. `MQTT_GRAPHQL_LEFT_OUT` lists what the Specs have that thrapp can't
show.

### `convert-direction-arrows.ts`

Converts the raw, Figma-exported arrow `<path>`s in a mimic module's `DirectionArrows.vue` into `<line>` elements with a `marker-end` arrowhead, matching the hand-authored convention used across mimic modules.

**Usage:**

```bash
pnpm convert-direction-arrows <module>

# Example
pnpm convert-direction-arrows dc
```

`<module>` is the folder name under `src/modules/thrapp/mimics/modules/<module>/layers/DirectionArrows.vue`.

**What it does:**

1. Reads the module's `DirectionArrows.vue` and locates every `<path>` with `fill-opacity="0.55"` (the signature of a Figma-exported arrow: an end-cap square, a chevron, and a thin rectangle spanning the arrow's length).
2. Parses each path's `d` attribute (supports absolute `M`/`L`/`H`/`V`/`C` commands) to recover the rectangle's two endpoints and locate the chevron subpath (identified by its cubic-bezier `C` commands).
3. Determines which endpoint carries the arrowhead by finding the endpoint closest to the chevron, then emits `x1`/`y1`/`x2`/`y2` for a `<line>` with the arrowhead end as `x2`/`y2`.
4. Merges a shared `flows-dir-arrow` marker (using the `stroke-flows-pipe-arrow` token) into the file's `<defs>`, alongside any pre-existing defs (e.g. Figma reference-image patterns), and wraps all lines in a single `<g marker-end="url(#flows-dir-arrow)">`.
5. Preserves any non-arrow content (e.g. a reference-image `<rect>`) unchanged, and formats the result with Prettier.

Paths without a detectable chevron are left untouched and reported as skipped — this can happen if the file mixes arrow paths with unrelated translucent shapes.

**Note:** this only handles the raw Figma export shape. Run it once per module right after pasting in the exported SVG, before any manual position tweaks.
