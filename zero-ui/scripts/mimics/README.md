# Mimic Data Workflow (Google Sheet driven)

The mimic data files under `src/modules/thrapp/mimics/modules/<module>/data/**` (e.g.
`dhw/data/boiler-tanks/_1054.ts`) are normally generated from a Google Sheet instead of being
hand-written.

```
schema.graphql ──┐
existing dhw/    ─┤ pnpm generate-sheet-tabs ──► scripts/mimics/mimic-out/*.csv
thrusters data  ─┘        (import into Google Sheet tabs)
                                 │
                                 ▼
                        Google Sheet workbook
                        ┌ Schema ──────── import schema-catalog.csv (dictionary)
                        │ Templates ───── import component-templates.csv (per-type slots)
                        │ Instances ───── import instances.csv (entities to build)
                        │ FillIn ──────── join formula → rows the designer fills in
                        │                 export FillIn tab as CSV
                                 ▼
                        pnpm generate-mimic-data <fillin.csv> [module]
                                 │  writes modules/<module>/data/**/*.ts
                                 ▼
                        pnpm roundtrip-mimic  (acceptance test, must stay green)
```

## Files

| File | Purpose |
|------|---------|
| `generate-sheet-tabs.ts` | Rebuilds the four CSVs below from `schema.graphql` + committed dhw/thrusters data. |
| `generate-mimic-data.ts` | Writes `data/**` from a filled-in sheet export. |
| `roundtrip-mimic.ts` | Acceptance test: regenerates dhw/thrusters from the seed and compares with committed code. |
| `lib/` | Shared library (parser, generator, schema catalog). |
| `mimic-out/schema-catalog.csv` | Every datapoint in the API (`module, section, field, componentType, valveType, yardTag, technicalName, friendlyName`). The dictionary of what can be referenced; the yard tag identifies most datapoints. |
| `mimic-out/component-templates.csv` | Per `MimicComponentType`: required field slots (`source`, `sensors.*`, `controls.*`, `parameters.*`, `controllerState.*`, `custom.*`), allowed types per slot, required flag, default tooltip. |
| `mimic-out/instances.csv` | The entities to build (`module, folder, key, componentType, title, ...`). An asset, actuator, sensor or circuit is just one kind of instance here. This is the list the designer edits to add new mimics. |
| `mimic-out/fillin-seed.csv` | Worked example (existing dhw/thrusters wiring) in exactly the format the generator consumes. |
| `mimic-out/roundtrip/` | Output of `pnpm roundtrip-mimic`; never touches the real `data/` dirs. |

## Step 1 — Generate the CSVs

```bash
pnpm generate-sheet-tabs
```

## Step 2 — Build the Google Sheet

Create a workbook with four tabs and import the CSVs into them
(File → Import → Upload → "Replace current sheet" into a tab with that name):

| Tab | Source | Column layout (row 1 = header) |
|-----|--------|--------------------------------|
| `Schema` | `schema-catalog.csv` | A module, B section, C field, D componentType, E valveType, F yardTag, G technicalName, H friendlyName |
| `Templates` | `component-templates.csv` | A componentType, B slotId, C slotLabel, D kind, E valueKind, F allowedFieldTypes, G required, H tooltipTitle, I tooltipComponentType |
| `Instances` | `instances.csv` | A module, B folder, C key, D componentType, E title, F tooltipTitle, G tooltipComponentType, H tooltipTechnicalName, I slots |

- **Schema** is a read-only dictionary.
- **Instances** is where you add new entities. Fill column I (`slots`) with the `;`-separated
  slotIds the instance uses — **the FillIn formula joins on this column; if it's blank, that
  instance produces no rows.**
- **FillIn** is created by two formulas (below). Columns A–M spill from the formula and are
  read-only; columns N–Y are plain empty cells for you to fill by hand — typing there can never
  break the formula.

### The FillIn tab formulas

**Cell `A1`** — header row:

```sheets
={"module","folder","instanceKey","componentType","title","tooltipTitle","tooltipComponentType","tooltipTechnicalName","slotId","slotLabel","kind","valueKind","fieldType","fieldName","sourceModule","customTitle","customYardTag","customTechnicalName","literalValue","refTarget","pidType","pidControllerField","pidSetpointField","pidOutputMinimumField","notes"}
```

**Cell `A2`** — the join formula:

```sheets
=LET(
  inst,  FILTER(Instances!A2:I, Instances!A2:A<>""),
  tmpl,  FILTER(Templates!A2:I, Templates!A2:A<>""),
  ni,    ROWS(inst),
  nt,    ROWS(tmpl),
  rowsI, TOCOL(MAKEARRAY(ni, nt, LAMBDA(r, c, r)), 1),
  colsT, TOCOL(MAKEARRAY(ni, nt, LAMBDA(r, c, c)), 1),
  ok,    MAP(rowsI, colsT, LAMBDA(r, c,
    AND(
      INDEX(inst, r, 4) = INDEX(tmpl, c, 1),
      ISNUMBER(FIND(";" & INDEX(tmpl, c, 2) & ";", ";" & INDEX(inst, r, 9) & ";"))
    ))),
  fi,    FILTER(rowsI, ok),
  fj,    FILTER(colsT, ok),
  MAP(fi, fj, LAMBDA(r, c,
    HSTACK(
      INDEX(inst, r, 1),
      INDEX(inst, r, 2),
      INDEX(inst, r, 3),
      INDEX(inst, r, 4),
      INDEX(inst, r, 5),
      INDEX(tmpl, c, 8),
      INDEX(tmpl, c, 9),
      "",
      INDEX(tmpl, c, 2),
      INDEX(tmpl, c, 3),
      INDEX(tmpl, c, 4),
      INDEX(tmpl, c, 5),
      IFERROR(INDEX(SPLIT(INDEX(tmpl, c, 6), ";"), 1, 1), "")
    )
  ))
)
```

It cross-joins every instance with every template slot whose `slotId` appears in the instance's
`slots` column, emitting one read-only row per (instance × slot): instance identity, tooltip
defaults, slot metadata, and `fieldType` (the slot's first allowed type). Adding a row to
**Instances** automatically expands **FillIn**.

> Fallback: paste `fillin-seed.csv` directly into the FillIn tab instead of using the formula,
> then add rows by hand.

## Step 3 — Fill in the FillIn tab

One row per (instance × slot). Fill columns N–Y:

- `fieldName` (N) — the schema datapoint, usually matched on the `Schema` tab via
  `module + instanceKey + componentType`.
- `sourceModule` (O) — which module owns the datapoint; usually same as column A. Override when
  referencing another module's field (e.g. thrusters seawater circuit → dhw's `adsorptionDelta`).
- `custom.*` slots (e.g. `custom.circuitName`, `custom.tankStateField`) → `literalValue` (S).
- Enum slots (`custom.sideA`/`sideB`) → `refTarget` (T), e.g. `enum:HeatExchangerPortOrientation.Side`.
- Controller refs (`custom.controller`, `custom.flowController`, `controllerState.controller`) →
  `refTarget` = controller name, plus the `pid*` columns (U–X).
- `custom.exchangeCircuit` / `custom.tankController` → `refTarget` = the referenced instance key.

## Step 4 — Export & generate

1. Export the FillIn tab as CSV (File → Download → Comma-separated values).
2. ```bash
   # all modules present in the CSV / or a single one:
   pnpm generate-mimic-data /path/to/fillin.csv [module]
   ```
   This writes `src/modules/thrapp/mimics/modules/<module>/data/**` (`_<key>.ts` per instance,
   folder `index.ts`, `controllers/index.ts`, `data/index.ts`). It overwrites the folder's
   `data/**` and validates every selected field against the schema.
3. Run `pnpm typecheck`.

## Step 5 — Verify

```bash
pnpm roundtrip-mimic
```

Regenerates dhw/thrusters into `mimic-out/roundtrip/` and asserts they are semantically identical
to the committed code. Keep it green after any change to generator or data model.

---

When schema, code, mimic data or design changes break this workflow, feed
[MAINTENANCE_INSTRUCTIONS.md](./MAINTENANCE_INSTRUCTIONS.md) to an agent to bring everything back
in sync.
