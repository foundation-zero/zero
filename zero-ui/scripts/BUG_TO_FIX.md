# Bugs & Inconsistencies Found

Notes collected while building the mimic-data pipeline. These are pre-existing inconsistencies in
the codebase or latent issues in the new tooling that a developer should review. Severity is my
judgement; none block the current pipeline (round-trip is green), but several are worth fixing.

---

## 1. Instance filename ≠ map key (alias imports)

`src/modules/thrapp/mimics/modules/dhw/data/exchange-circuits/`
- file `_dc.ts` is imported as `_brightloop` and keyed as `brightloop`:
  `import _brightloop from "./_dc";` then `brightloop: _brightloop`.

`src/modules/thrapp/mimics/modules/dhw/data/connecting-circuits/`
- file `_freshwater.ts` is keyed as `domestic`: `domestic: _freshwater`.

The filename and the index key disagree. The parser had to learn to resolve import aliases to
filenames. **Fix:** rename the files to match their keys (`_brightloop.ts`, `_domestic.ts`), or make
the key equal the filename. This also makes the generator output and committed layout consistent.

---

## 2. Factory folders (no per-instance files)

Thrusters `check-valves/index.ts` and `manual-valves/index.ts` build instances programmatically:
```ts
const ids = [...];
Object.fromEntries(ids.map((id) => [id, checkValve(id)]))
```
Every other folder uses one `_<key>.ts` file per instance. The parser/generator had to special-case
this factory pattern (and it only handles the simple "custom source + empty sections" shape — a
factory with richer fields would need more work). **Fix (optional):** convert these two folders to
the standard per-file layout, or formalise the factory pattern.

---

## 3. Data constant naming is inconsistent (folder name ≠ constant name)

The constant exported per folder does not follow a single rule:
- `boiler-tanks/` → `DHW_TANK_DATA` (not `BOILER_TANKS`)
- `connecting-circuits/` → `DHW_FRESHWATER_CIRCUIT_DATA` (not `CONNECTING_CIRCUITS`)
- `exchange-circuits/` → `EXCHANGE_CIRCUIT_DATA` (singular)
- `level-switches/` → `LEVEL_SWITCHES_DATA` (plural) but `level-sensors/` → `LEVEL_SENSOR_DATA`
- `assets/` → `ASSET_DATA` (singular)

The generator hard-codes a `FOLDER_SUFFIX` map in `scripts/mimics/lib/generate.ts` to reproduce these.
**Fix:** adopt one rule (e.g. always singular, folder-derived) and remove the exception map, or
document the mapping. New folders must remember to add a suffix entry.

---

## 4. Index key ordering is arbitrary (insertion order, not sorted)

Many `data/<folder>/index.ts` files list keys in non-alphabetical insertion order (e.g. dhw
`switch-valves`: 11,12,14,13,7,8,10,9,3,4,6,5,17,16,18). The generator emits keys in the order they
appear in the FillIn CSV, so round-trips are stable, but this is noisy. **Fix:** sort keys.

---

## 5. Instance section ordering is inconsistent

Across instance files the six sections appear in different orders:
- `_1053.ts` (BoilerTank): `custom, controls, controllerState, parameters, source, sensors`
- `_1022.ts` (Pump): `custom, controllerState, source, controls, parameters, sensors`
- `_1004.ts` (HeatExchanger): `controls, controllerState, custom, source, parameters, sensors`

The generator always emits one canonical order. Functionally irrelevant, but the committed files
don't match each other. **Fix:** normalise to one order.

---

## 6. `fieldTooltip` requires its content argument

`src/modules/thrapp/mimics/modules/shared.ts`:
```ts
export const fieldTooltip = <Type, Module>(field, content: Partial<TooltipContent>) => ...
```
`content` is required (not optional). The generator therefore **must** always emit
`fieldTooltip(this.source, { ... })` with at least one property, or it produces
`fieldTooltip(this.source)` which fails to typecheck. A component type with no title/componentType/
technicalName would hit this. **Fix:** make `content` optional in `fieldTooltip`, or guarantee every
tooltip has content.

---

## 7. Tooltip `technicalName` is inconsistent

Only the freshwater circuit tooltip carries `technicalName`
(`_freshwater.ts`: `fieldTooltip(this.source, { title: "Fresh water", technicalName: "fresh-water" })`).
The other shared `tooltip()` helpers omit it. It works, but the pattern is uneven and the generator
had to add a `tooltipTechnicalName` column just for this one case. **Fix:** decide whether
`technicalName` belongs in tooltips and apply consistently.

---

## 8. Cross-module field reference with a TODO

`src/modules/thrapp/mimics/modules/thrusters/data/exchange-circuits/_seawater.ts:16`
```ts
deltaT: getField(SensorComponentType.DeltaT, "dhw", "adsorptionDelta"), // TODO
```
The thrusters seawater exchange circuit reads a delta-T datapoint that lives in the **dhw** module
(`adsorptionDelta`). This is a deliberate but fragile cross-module reference; the schema has no
`thrustersDelta`. **Fix:** confirm the correct datapoint for thrusters (or that the dhw one is
intended) and remove the TODO.

---

## 9. Schema inconsistency: `pvtMixMainAft` has `componentType: null`

`src/modules/thrsim/graphql/schema.graphql:1241`
```
pvtMixMainAft: SensorValveType! @jsonSchemaDirective(yardTag: "50001044-02", componentType: null, valveType: "mix")
```
Every other `SensorValveType` has `componentType: "valve"`; this one is `null`. The codegen
(`consts.generated.ts`) therefore omits `componentType` for this field, and the catalog marks it as
`componentType: null` / unmapped. **Fix:** set `componentType: "valve"` in the schema (line 1241).

---

## 10. The "yard tag in the identifier" rule does not hold for calculated/parameters

Auto-suggesting the FillIn field by `module + yardTag + componentType` works for instrumented
sensors/actuators, but:
- **Parameters** have no yard tag at all (they are config values, not physical instruments).
- **Calculated** datapoints (e.g. `thrustersTemperatureRecovery`,
  `thrustersTemperaturePreCooler`, `thrustersFlow`, `dhwFreshwaterFlowSupply`) have an empty
  `yardTag: ""` in the schema.

These rows come back blank in the FillIn suggestion and must be selected manually. Not a bug per se,
but a UX gap — the suggestion logic will not auto-fill them.

---

## 11. `componentType` is duplicated across sections for the same physical device

The same yard tag appears in both `sensorValues` and `controlValues` (e.g. a valve is
`sensor:valve` and `control:valve`), and some fields recur across modules (e.g. `recoveryTemperature`
in several `parameters` types). The FillIn suggestion matches on `module + yardTag + componentType`,
which disambiguates these in practice, but be aware the Schema dictionary is not unique on
`yardTag` alone.

---

## 12. Generated output diverges from committed conventions (intentional, but note)

- The generator **inlines** tooltips and all fields per instance and does **not** produce
  `shared.ts`. The committed code hoists common fields/tooltips into `shared.ts` and references them.
  Functionally equivalent, but regenerating a folder deletes its `shared.ts` and changes the file
  layout. If the team wants to keep the `shared.ts` style, the generator needs a hoisting step.
- `instances.csv` `title` is machine-derived (e.g. "Switch Tank3 Inlet") for instances whose source
  is a schema field; custom-title instances (e.g. tanks) keep their nicer titles. Cosmetic.
