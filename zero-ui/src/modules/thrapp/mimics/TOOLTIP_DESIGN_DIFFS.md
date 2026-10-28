# Tooltip design differences

Differences between the mimic tooltip designs and the current implementation in
`src/modules/thrapp/mimics/tooltips/`.

Design: [Mouse-click inf 1.1 designs](https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=10139-384795)

Compared against the Vue templates and `src/modules/thrapp/i18n/en.json`, not against the running
app. Items marked _verify_ depend on runtime data and need checking in the browser.

## General

- [ ] `items.automatedControl` reads "Automated control"; the design says "Automatic control".
- [ ] Most tooltips render a `SensorGraph` that does not appear in any design. Probably
      intentional; confirm with design.
- [ ] `ExchangeCircuitPartial` renders the heat exchange source as "(Calculated)" with
      parentheses. The design (and `HeatExchangerTooltip`) shows "Calculated" without them.

## PID controller partial

Used by Pump, Flow valve, Heat pump, and the Temperature/Flow/Pressure sensor tooltips.

- [ ] The target row is labelled "Target" (`items.target`); the design says "Setpoint".
- [ ] _Verify_: the design shows "This component" as the Actuator source on the actuator's own
      tooltip and as the Measurement source on the sensor's own tooltip. The code always renders
      `api-only` sources.

## Tank (`BoilerTankTooltip`)

- [ ] Input → State source reads "Tanks controller" (`sources.tankState`); the design says
      "Tank controller".
- [ ] The Level sensor value is hardcoded as `Not empty` instead of coming from data.
- [ ] "Min. temperature" / "Max. temperature" have dots; the design has "Min temperature" /
      "Max temperature".
- [ ] The Controls block is missing the "Tank state" row at the top of the controller group.

## Switch valve (`SwitchValveTooltip`)

- [ ] Input → Setpoint source is hardcoded to "This component" (`sources.this`); the design shows
      the controlling controller ("Tank controller" / "Boost mode").
- [ ] Missing the **"Boost mode – switch valves"** controls variant: a Module mode badge plus the
      `dhw-switch-low-temperature`, `dhw-switch-heatpump` and `dhw-switch-high-temperature` states.
      The code only handles `custom.tankController`.

## Flow valve (`FlowControlValveTooltip`)

- [ ] Input → Setpoint source is "This component"; the design shows the PID controller name
      (e.g. "DC flow controller").
- [ ] Uses `Partials.SubmitButton` where every other tooltip uses `SubmitControlForm`. Not a design
      difference, but inconsistent.

## Pump (`PumpTooltip`)

- [ ] "Relative duty point" renders as "Dutypoint" (`items.relativeDutyPoint`).
- [ ] Output is missing **Total running hours**.

## Heat pump (`HeatPumpTooltip`)

- [ ] Input: the design has **State** (source "Heatpump controller", Active badge). The code has an
      editable "On-off" with no source.
- [ ] The **Output** section is missing: Energy consumption, Power input, Operation time,
      Total running hours.
- [ ] The Controls header is missing the "View controls" action.

## HVAC (`HVACTooltip`)

- [ ] Missing the Automatic control / "Switch to manual mode" row (`ManualControl`).

## DC converter (`DcConverterTooltip`)

- [ ] No yard tag next to the instance.
- [ ] Output rows are "Power" and "Internal temp"; the design has "Temperature internal" followed by
      "Electric consumption".

## Thruster (`ThrustersTooltip`)

- [ ] No yard tag next to the instance.
- [ ] Power and Internal temperature are still wired to `placeholder` fields.
- [ ] Label is "Internal temp" (`items.internalTemperature`); the design says
      "Temperature internal".

## PVT (`PvtTooltip`)

- [ ] No yard tag next to the instance.
- [ ] The button says "Switch to circuit mimic"; the design says **"View PVT bimini mimic"** and
      places it as its own row above the Heat exchange header.

## Connecting circuit (`ConnectingCircuitTooltip`)

- [ ] The design groups rows under **Temperature** (incoming/outgoing) and **Flow**
      (incoming/outgoing). The code reuses `ExchangeCircuitPartial`, which shows heat exchange,
      delta T and a single flow.

## Exchange circuit (`ExchangeCircuitTooltip`)

- [ ] The design has no Heat exchange row, and Delta temperature has a "Calculated" source. The code
      shows a Heat exchange row and Delta temperature without a source.

## Consumer (`FreshwaterCircuitTooltip`)

- [ ] The design has no component info block; the code renders `ComponentInfo`.
- [ ] The design groups rows under **Temperature** and **Flow** sub-headers; the code is a flat list
      that alternates temperature and flow.

## Temperature sensor (`TemperatureSensorTooltip`)

Only a generic `custom.controller` PID is supported. Missing controller variants:

- [ ] **"Tanks controller – temperature"**: Actuator (Tank state), Sensors (Temperature), Targets
      (minimum/maximum tank temperature), Error (minimum/maximum temperature).
- [ ] **"Boost mode"**: Actuator (Circuit mode badge), Sensors (Temperature), Targets (Boosting
      delta, High temperature circuit), Error (Temperature difference – Boosting delta).

## Pressure sensor (`PressureSensorTooltip`)

- [ ] Missing the **"Tanks Pressure sensor"** variant: Output shows **Level** (L) instead of
      Pressure, plus a "Tanks controller – Levels" controls block (Tank state, Level, min/max tank
      level targets, min/max level error).

## Matching the design

Heat exchanger, PCM (Flextherm Eco G2), Flow sensor, Level sensor / level switch and Manual
switch valve have no obvious differences.
