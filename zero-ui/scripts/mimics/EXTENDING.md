# Extending the Mimic Data from a Filled Plan

**Audience: a front-end developer and/or their AI agent.** Input is a validated plan CSV
(exported from the mimic Google Sheet, checked with `pnpm verify-plan`). Output is hand-written
code under `src/modules/thrapp/mimics/modules/<module>/data/**`. Nothing here is generated —
you write the code, the sheet only tells you exactly what it must contain.

Usage of the sheet itself is documented in [README.md](./README.md).

## Reference material (read before starting)

| What | Where |
|------|-------|
| Slot definitions per component type (the authority) | `src/modules/thrapp/types/fields.ts` |
| Component type enum | `src/modules/thrapp/types/index.ts` |
| `getField` / `getCustomField` providers | `src/modules/thrapp/mimics/providers` |
| Worked examples | `src/modules/thrapp/mimics/modules/dhw/data/**`, `modules/thrusters/data/**` |
| Sheet format + value conventions | `scripts/mimics/README.md` |
| Canonical slot table (mirrors fields.ts) | `scripts/mimics/lib/templates.ts` |

## Reading a plan row

One row = one slot of one instance. Group rows by (`module`, `folder`, `key`); every group
becomes **one file**: `data/<folder>/_<key>.ts`. The row tells you:

- `componentType` → the `MimicComponentType` generic of `toInstance<...>`
- `slotId` → where in the instance object the value goes: `sensors.level` →
  `sensors: { level: ... }`; bare `source` → `source:`; etc.
- `valueKind` → how to interpret `value`:

| valueKind | Code |
|-----------|------|
| `field` | `getField(<Enum>.<Member>, "<module>", "<value>")` — resolve `<Enum>.<Member>` from the row's `allowedFieldTypes` via the maps in `scripts/mimics/lib/enums.ts` (e.g. `sensor:temperature` → `SensorComponentType.Temperature`). A `module:value` datapoint keeps its module as first argument even if it differs from the instance's module. |
| `customSource` | `getCustomField("<module>", { title: <srcTitle>, yardTag: <srcYardTag>, technicalName: <value> })` — omit title/yardTag when empty. |
| `literal` | plain string literal |
| `enum` | member of `HeatExchangerPortOrientation` (import from `mimics/components/heat-exchanger`) |
| `controllerRef` | identifier of a PID controller in `data/controllers/index.ts` (see below) |
| `instanceRef` | getter returning the referenced instance's data (see below) |

## Step by step

1. **Scope**: work module by module (`module` column). Never touch modules outside the CSV.
2. **Controllers** (`controllerRef` values with no matching export yet): add an exported
   constant to `data/controllers/index.ts`, following the existing style:
   ```ts
   export const pumpFlowController: PIDController<SensorComponentType.Flow> = {
     type: SensorComponentType.Flow,
     controller: getField(ControllerStateComponentType.PIDController, "dhw", "dhwPumpFlowController"),
     setpoint: getField(ParametersType.Flow, "dhw", "heatpumpFlowSetpoint"),
     outputMinimum: getField(ParametersType.FlowControl, "..."), // optional
   };
   ```
3. **New folders**: if `folder` has no directory under `data/`, create it with an `index.ts`
   that maps keys via `toFieldsMap({ [MimicComponentType.<Type>]: { ... } })` — copy an existing
   folder index. Constant/data naming follows the folder's neighbours.
4. **Instance file** per group: `data/<folder>/_<key>.ts`:
   ```ts
   export default toInstance<MimicComponentType.BoilerTank>({
     custom: { tankStateField: "tank2State" },
     controls: {},
     controllerState: {},
     parameters: {},
     source: getCustomField("dhw", {
       title: "Tank 2",
       yardTag: "1054",
       technicalName: "hot-water-tank-2",
     }),
     sensors: { ... },
     get tooltip() {
       return tooltip(this.source);
     },
   });
   ```
   - Include all six section keys even when empty (match existing files).
   - Empty plan cells → leave that slot out or leave the section empty; never invent values.
5. **Tooltips are derived**, never authored: use the folder's shared `tooltip(this.source)`
   helper (see any existing folder's `shared.ts`). Only deviate when an existing neighbour does.
6. **Cross-instance refs** (`@instance:<key>`): emit a getter deferring resolution, like the
   heat-exchanger example:
   ```ts
   get exchangeCircuit() {
     return DHW_EXCHANGE_CIRCUIT_DATA[MimicComponentType.ExchangeCircuit].adsorption.sensors;
   }
   ```
7. **Hoisting**: identical `getField(...)` calls repeated across instances of a folder go into
   that folder's `shared.ts` (e.g. shared parameters, shared sensor readings). Keep it faithful:
   same field, same module.
8. **Register** every new instance in its folder's `index.ts`.

## Out of scope (do not infer from the sheet)

- Layout customs (`width`, `height`, `forceHeight`) — developer judgement; ask if a new circuit
  looks wrong.
- App wiring: mimic `.vue` page, `layers/`, registration in
  `src/modules/thrapp/views/Mimic.vue`.
- Backend/schema changes: if a needed datapoint is missing from the Schema tab, stop and report.

## Verification (mandatory)

```bash
pnpm typecheck
pnpm verify-plan --check /path/to/plan.csv [controllers.csv]
```

- `typecheck` must pass.
- `--check` re-parses the committed data and diffs it against the sheet — every filled cell
  must be observable in code and code must not contain content the sheet doesn't declare.
  Warnings about missing `srcTitle` on valves/sensors copied from existing patterns are OK;
  errors are not.

## Worked example

Plan rows for dhw BoilerTank key `1054` (from `mimic-out/plan-seed.csv`) produce exactly
`src/modules/thrapp/mimics/modules/dhw/data/boiler-tanks/_1054.ts`. Compare them side by side
before writing anything new.
