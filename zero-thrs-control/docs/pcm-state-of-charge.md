# PCM state of charge

The Flamco FlexTherm Eco 9E has no communication interface, so state of charge has to be
estimated from our own supply temperature, return temperature and flow. `PcmChargeController`
integrates measured heat and re-anchors the integral to empty or full whenever a module's
outlet converges on its inlet — the only observable that says the 58 °C phase change has
run out.

## The hardware

The cell holds 110 kg of PCM58, whose phase transition is at 58 °C (Flamco FlexTherm Eco
manual, ch. 1). Two hydraulically independent exchangers sit in it.

| Spec (9E)                   | Value                | Why it matters                                |
| --------------------------- | -------------------- | --------------------------------------------- |
| Phase change temperature    | 58 °C                | The plateau everything anchors on              |
| PCM mass                    | 110 kg               | Latent share is roughly 7 kWh                  |
| Nameplate capacity          | 10,5 kWh             | Rated 75 °C charge, 10 → 40 °C tapwater draw-off. Not our duty |
| Discharge water temperature | 50 – 55 °C           | Kills any absolute empty-threshold on the outlet |
| Thermal charging supply     | min 65 °C, max 80 °C | `minimum_charging_temperature` was 60          |
| Standing loss               | 0,77 kWh/24h = 32,1 W | Idle decay term                               |
| LPC circuit (B–C)           | 3,5 l, 18 kW         | Module 1's thrs-side volume                    |
| HPC circuit (A–D)           | 6,8 l, 35 kW         | Added in parallel on modules 2–4               |
| Recommended max flow        | 20 l/min             | We run 5 l/min, so residence time is long      |
| Electric element            | 2,8 kW               | Invisible to a hydronic energy balance         |

The nameplate figure is worth spelling out, because using it would make a genuinely full
module read about 65 %. The manual defines it as the energy drawn off by 10 °C mains water,
after a 75 °C charge, until the outlet falls to 40 °C. We charge to 65–70 °C and discharge
into a loop that already returns around 50 °C, so the low-grade tail that makes up that
rating is unreachable. What is usable is essentially the latent plateau, which is why
`PCM_MODULE_CAPACITY` is 7 kWh and carries a TODO.

Neither document mentions supercooling.

## Getting data out of the unit

There is no communication interface. The A2.ET controller documents exactly three external
things, and two of them are inputs.

| Interface                              | Terminal            | Direction         |
| -------------------------------------- | ------------------- | ----------------- |
| Boost (temporary)                      | 1 to 2 (0V), J1.6 FV | Input, volt-free |
| Charge enable / PV signal              | 3 to 4 (0V), J1.7 FT | Input, volt-free |
| Front LEDs: Power, >50%, >100%, Heating | D4, D3, D2, D1     | Indication only   |

So the unit's own notion of charge is three coarse levels: below 50 %, above 50 %, above
100 %. The manual does confirm the unit measures charge state internally — *"uitgerust met
temperatuursensoren voor het meten van de laadtoestand"* — via a 2-core and a 4-core probe
wired to J1.1–1.3 and J9.1. That measurement simply never leaves the box.

Three things the engineers could do, cheapest first.

1. **Tap the LED drive lines** into optocoupled digital inputs. Gives >50 % and >100 % as a
   coarse ground truth, and D1 "Verwarming" tells us when the 2,8 kW element is drawing.
   That maps straight onto the existing `sensor.Pcm.charged` input, which is hardwired
   `False` today.
2. **Fit our own probe in the thermowell.** The sensor replacement guide shows the 4-core
   probe is a field-replaceable wire pushed into a copper pocket to a set depth, 710 mm on
   the 9E. If the pocket takes a second probe, a Pt1000 of ours reads PCM core temperature
   directly and the melt plateau becomes directly observable instead of inferred. This is
   the one that would actually make the estimate good.
3. **Ask Flamco whether the PCB has an undocumented serial header.** The board is built by
   Sunamp, whose later products do have comms.

Driving terminal 3–4 from our control is also worth taking while we are in there: it gives
us the charge enable, so the element stops charging against our wishes.

The element matters more than it looks, because its heat goes straight into the cell and
so never appears in any circuit. In the final configuration only module 1 has one
connected and we drive it through a digital output (`pcm_module1.on`).
`PcmChargeController` reads that same output and adds 2,8 kW to the balance while it is
set, which is the only reason the integral survives an electric boost. Modules 2–4 have no
element, so their `heating_power` is zero.

Three caveats. The command is not the draw: the unit's own thermostat can open the element
while our output stays closed, and the balance then counts 2,8 kW that is not flowing. A
contactor auxiliary or the D1 "Verwarming" LED would fix that, which is another reason to
want option 1 above. Commissioning data recorded before this was wired has PCM 1 and PCM 2
both heating with nothing recorded either way, so it cannot validate the integral. And
nothing commands the output yet: when to boost electrically is a separate decision from
estimating the charge, and probably belongs with the PV surplus logic.

## Topology on board

The manufacturer labels the four ports A = cold in (HPC), B = cold in (LPC), C = warm out
(LPC), D = warm out (HPC).

| Module  | Thrs loop                            | Freshwater      | Purge volume |
| ------- | ------------------------------------ | --------------- | ------------ |
| 1       | B in, C out (LPC only)               | D in, A out (HPC) | 3,5 l      |
| 2, 3, 4 | B and D in, A and C out (LPC ∥ HPC)  | —               | 10,3 l       |

One thing to verify with the engineers: on every module the HPC is connected against its
labels, cold entering the port marked "warm uit". On modules 2–4 that means the two
exchangers run in opposite internal directions. It may be deliberate or an as-built drawing
convention, but if the ports reflect an internal top/bottom arrangement it would cost
performance.

## How the estimate works

A PCM module has three regimes, and only one observable separates them.

| Regime              | Stored energy | Outlet temperature                                |
| ------------------- | ------------- | ------------------------------------------------- |
| Solid, sensible     | ≈ 0           | Tracks the inlet freely                           |
| Melting or freezing | 0 → 100 %     | Pinned near 58 °C while any solid or liquid remains |
| Liquid, sensible    | ≈ 100 %       | Tracks the inlet again                            |

Inside the plateau, temperature carries no information about how far the phase front has
travelled. Only integrated heat does. At the ends of the plateau it is the reverse: the
integral has drifted, and the temperature says exactly where you are. So each is used for
what it is good at.

1. **Integrate** the measured heat continuously, clamped to `[0, capacity]`.
2. **Re-anchor** to 0 or capacity when the outlet converges on the inlet while the inlet is
   clearly past the melt point, held for `PCM_ANCHOR_DWELL`.
3. **Hold** through idle, minus the 32,1 W standing loss.
4. **Report `None`** until the first anchor fires, rather than inventing 50 %.

The anchor test is the part that took the most revision. The intuitive version — outlet
above 58 + ε means charged — fails twice: the inlet is already 65 °C from the first minute
of charging, and the datasheet's 50–55 °C discharge outlet is an exchanger approach
temperature, not a state of charge. What holds in both directions is that the module stops
exchanging heat when it has nothing left to melt or freeze:

```
|T_out - T_in| < PCM_EXHAUSTED_DT  and  T_in > 58 + 3  =>  full
|T_out - T_in| < PCM_EXHAUSTED_DT  and  T_in < 58 - 3  =>  empty
```

That is gated on flow rather than on `PcmChargingState`. As ΔT collapses the heat falls
below the 100 W deadband and the state flips to idle, which would otherwise race the dwell
timer and stop the anchor ever firing.

Three practical guards:

- The sensors sit in the pipework and read stale without flow, so a circuit volume has to be
  purged before its ΔT means anything. `_settle` counts integrated litres since flow start
  rather than using a fixed timer, so the wait scales with the flow that is actually
  clearing the pipes.
- `dt` comes from `heat.timestamp`, which `Stamped.combine` sets to the oldest contributing
  sensor, and nothing is integrated across a gap over `PCM_MAX_SAMPLE_GAP`.
- The flowmeters' own temperature readings are unreliable, so the consumers-return mix uses
  the dedicated 1038-xx sensors only.

Module 1 is passed two circuits, because the freshwater system can draw it down with the
thrs loop idle. If the two disagree — one converged hot, the other converged cold — neither
anchors. It is also passed its element's feedback, and counts 2,8 kW into the cell while
that is on, with no flow required. The anchors are deliberately left alone: a converged ΔT
still means the water found nothing to melt or freeze, whether or not the element is
running.

The capacity constant calibrates itself for free: the energy integrated between a full
anchor and the next empty anchor *is* that module's usable capacity under our actual duty.
`energy` is logged in joules alongside the ratio, so a corrected capacity can be applied
retrospectively in Greptime without re-running anything.

## What changed

- `units.py` — corrected the `WATER_HEAT_TRANSFER_CONVERSION` comment, which said
  kW·min/(l·K) for a value that is W/((l/min)·K). Added
  `GLYCOL_20_HEAT_TRANSFER_CONVERSION` at 66,2, about 5 % below water, with the mixture
  flagged as an assumption. Added `OptionalRatio` and `OptionalJoule`.
- `definitions/controllers.py` — replaced `PCM_CHARGE_FULL_TEMP` and
  `PCM_CHARGE_EMPTY_TEMP`, both 51 and both marked TODO, with the melt point, margins,
  dwell, purge volumes, standing loss and capacity. `PcmChargeControllerValues` gained
  `energy` and `charged`, and `charge` became optional.
- `control/controllers.py` — `PcmChargeController` rewritten. The old charge test was also
  inverted: above full temperature it set 0.0, above empty temperature 1.0.
- `input_output/modules/pcm.py` — the module inlet now follows `pcm_switch_charging_supply`
  and `pcm_switch_charging_return`, so it is the producers header while charging and the
  consumers-return mix otherwise. Added that mix as `pcm_temperature_consumers_return`, the
  five borrowed consumers sensors it needs, and `pcm_heat_module1_freshwater`. Module heat
  now uses the glycol conversion; the freshwater circuit stays on water. In simulation the
  borrowed sensors come off `pcm_consumers_supply`, which is the model's single consumers
  stream.
- `control/modules/pcm.py` — `minimum_charging_temperature` 60 → 65, per-module purge
  volumes, module 1 fed both circuits and the state of its element output.
- `tests/control/test_pcm_charge_controller.py` — 18 tests covering the anchors, the purge
  gate, the dwell, integration, standby loss, data gaps, the two-circuit cases and the
  heating element.
- `zero-ui` — schema re-exported, `PcmChargeController` TS type and its mimic mock updated.

## Still open

| Question                                                                            | Who                | Why it blocks                                          |
| ----------------------------------------------------------------------------------- | ------------------ | ------------------------------------------------------ |
| Can we tap the LED lines, fit a second probe in the thermowell, or is there a serial header? | Engineers, Flamco  | Decides whether we estimate or measure                 |
| What decides when module 1 boosts electrically?                                     | Us                 | The output exists and nothing drives it                |
| Is the HPC deliberately connected against its port labels?                          | Engineers          | Possible performance loss on all four modules          |
| Does PCM58 supercool on discharge?                                                  | Flamco, Sunamp     | A freeze plateau below 58 °C would false-trigger the empty anchor |
| Ethylene or propylene glycol, and what concentration?                               | Us                 | Currently assumed 20 %, worth about 1 % either way     |
| When do the freshwater topics get fixed?                                            | Us                 | Module 1's balance is wrong without them               |
| Do we want a real feedback input for the element, or is the command good enough?    | Us, engineers      | Today the balance counts 2,8 kW whenever the output is set |

The first is the one worth pushing: a probe in the thermowell would turn this from an
estimate into a measurement. The rest is tuning.

Deliberately not done here:

- **Module selection still reads `sensor_values.pcm_moduleN.charged`**, not the estimator.
  The FMU drives that input, so flipping the source would change simulated control
  behaviour with no real-data validation behind it. `PcmChargeController.charged` is exposed
  and ready; switching `_set_supplying_flow_setpoints` and `_all_discharged` over to it is
  a follow-up, and note that an uncalibrated module must count as charged or it will never
  be discharged, never anchor, and never become known.
- **No persistence.** A restart comes up unknown until the first anchor.
- **`pnpm codegen` has not been run** in zero-ui; it needs `.env.local` and an endpoint.
  Nothing surfaces `energy` in the UI yet.
- **Thresholds are not fitted to logged data.** What is in Greptime was recorded with the
  elements on for PCM 1 and 2 and no feedback on either, and holds no complete cycles, so
  there is nothing yet that would validate an anchor.

## Sources

- Flamco product sheet 18202, FlexTherm Eco 9E, 2023/05/03
- [Installatie- en bedieningshandleiding, art.nr 18200, 2022-03 NLD](https://flamco.aalberts-hfc.com/media/files/manuals/Man_FlexTherm_Eco_art.nr18200_2022-03_NLD.pdf)
- [QSG Temperatuursensoren v1.0](https://flamco.aalberts-hfc.com/media/files/manuals/QSG-electronic_FlexTherm_Eco_nld_v1.0.pdf)
- [QSG A2.ET Control Unit Replacement, 2020-10](https://flamco.aalberts-hfc.com/media/files/manuals/QSG_FlexTherm_Eco_Control_Unit_Replacement_2020-10.pdf)
