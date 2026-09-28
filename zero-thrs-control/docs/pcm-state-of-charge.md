# PCM state of charge

The four heat batteries on board are Flamco FlexTherm Eco 9E units, filled with a phase
change material (PCM). The unit measures its own charge internally, but it has no
communication interface. Control therefore estimates each module's state of charge from
the heat measured in the water through it: supply temperature, return temperature and flow.
The estimate is used to show how much energy is stored and, eventually, to choose which
module to charge or discharge.

## The unit

Each module holds 110 kg of PCM58, a material that melts and solidifies at 58 °C. Two
hydraulically independent heat exchangers run through the PCM cell. Flamco labels their
ports A–D: the A–D exchanger is the larger one ("HPC" in the manual) and the B–C exchanger
the smaller ("LPC").

| Spec (9E)                   | Value                | Relevance                                         |
| --------------------------- | -------------------- | ------------------------------------------------- |
| Phase change temperature    | 58 °C                | The plateau the estimate anchors on               |
| PCM mass                    | 110 kg               | Latent heat of roughly 7 kWh                      |
| Nameplate capacity          | 10.5 kWh             | Not reachable under our duty, see below           |
| Discharge water temperature | 50–55 °C             | Exchanger approach, not a measure of charge       |
| Thermal charging supply     | min 65 °C, max 80 °C | Manufacturer range for charging from water       |
| Standing loss               | 0.77 kWh/24h (32 W)  | Slow decay while idle                             |
| B–C exchanger               | 3.5 l, 18 kW         |                                                   |
| A–D exchanger               | 6.8 l, 35 kW         |                                                   |
| Recommended max flow        | 20 l/min             |                                                   |
| Electric element            | 2.8 kW               | Heats the cell directly, invisible in the water   |

The nameplate capacity is the energy delivered to 10 °C mains water, after a 75 °C charge,
until the outlet falls to 40 °C. We charge to 65–70 °C and discharge into a loop that
returns around 50 °C, so the low-temperature part of that rating is out of reach. What is
usable is essentially the latent heat of the melt, about 7 kWh per module.

## Topology on board

| Module  | Thrs loop                         | Freshwater          |
| ------- | --------------------------------- | ------------------- |
| 1       | B–C exchanger                     | A–D exchanger       |
| 2, 3, 4 | B–C and A–D exchangers in parallel | —                   |

On the thrs loop, the modules are charged from the producers header and discharged by the
return from the consumers. The inlet temperature of a module is therefore the producers
temperature while charging, and the flow-weighted mix of the consumers returns while
discharging. Module 1 can also be discharged by the freshwater system with the thrs loop
idle, so both of its circuits count towards its balance.

Only module 1 has its 2.8 kW electric element connected, switched by a digital output
from control.

## How the estimate works

A PCM module goes through three regimes, and temperature alone only distinguishes the
two ends:

| Regime              | Stored energy | PCM temperature                               |
| ------------------- | ------------- | --------------------------------------------- |
| Solid               | empty         | Below 58 °C, follows the inlet                |
| Melting or freezing | empty → full  | Held at 58 °C, whatever the phase fraction    |
| Liquid              | full          | Above 58 °C, follows the inlet                |

During the melt, the temperature says nothing about how much has melted; only the
integrated heat does. At the ends it is the other way round: the integral will have
drifted, but the temperatures say exactly where the module is. The estimate uses each for
what it is good at.

**Integrate.** Stored energy changes by the heat measured in each circuit through the
module, `flow × ΔT × heat capacity`, plus the element's power while it is switched on.
While nothing flows, the standing loss is subtracted. The result is clamped between empty
and full.

**Anchor.** A module is set to exactly full or empty when it stops exchanging heat with
water that is clearly past the melting point. The measure for this is the exchanger's
effectiveness, taking the PCM to be at 58 °C:

```
effectiveness = |T_out − T_in| / |T_in − 58 °C|
```

While the PCM melts or freezes it stays at 58 °C and pulls the outlet towards it, so the
effectiveness stays high. Once the latent heat is used up, the PCM moves towards the inlet
temperature and the effectiveness drops to zero. If it stays below a threshold for several
minutes, with the inlet a few degrees above 58 °C the module is full, and with the inlet
below 58 °C it is empty.

This ratio is used rather than ΔT or heat on its own. The heat depends on the flow and is
small at low flow even mid-melt. A fixed ΔT threshold means something different at a 62 °C
inlet than at a 75 °C one. The effectiveness does not depend on either. An absolute outlet
temperature also does not work: during a normal discharge the outlet sits at 50–55 °C
whatever the state of charge.

**Unknown until anchored.** Until a module has been seen full or empty, its energy has no
reference point and is reported as unknown rather than guessed. Module selection should
still discharge unknown modules, since that is how they anchor empty and become known.

Some practical details:

- The temperature sensors sit in the pipework, so without flow they read whatever water
  was last pushed past them. After flow starts, or after the inlet switches between
  producers and consumers, a circuit only counts once its exchanger volume has been
  flushed through. This is measured in litres, not seconds, so the wait scales with the
  flow.
- Nothing is integrated across gaps in the data.
- The loop carries 20 % glycol, whose heat capacity is about 5 % below that of water. The
  freshwater circuit is plain water.
- If two circuits through a module indicate opposite ends at the same time, neither
  anchors.
- The energy between a full anchor and the following empty anchor is the module's
  actual usable capacity. Energy is logged alongside the charge ratio, so a corrected
  capacity can be applied to historic data.

## Limitations

- The capacity per module is an estimate of the latent heat, not yet measured over a full
  cycle. The anchor thresholds are not yet fitted to logged cycles either.
- Control switches the element, but the unit's own thermostat can cut it out. The estimate
  counts the full 2.8 kW whenever the output is on.
- It is unknown whether PCM58 supercools on discharge. If it freezes below 58 °C, the
  empty anchor may fire early.
- After a restart, every module is unknown until its next anchor.
- The purge volumes include the exchangers but not the pipe runs to and from the modules.
- The A–D exchanger appears to be connected against its port labels on every module, with
  cold water entering the port marked "warm uit". If the ports reflect the internal layout,
  this costs performance. To be verified.
- Module selection does not use the estimate yet.

## Possible hardware improvements

The unit's A2.ET controller exposes only a boost input (terminals 1–2), a charge enable
input (3–4) and four front LEDs: Power, >50 %, >100 % and Heating. Cheapest first:

1. **Read the LED drive lines** through optocoupled digital inputs. This gives >50 % and
   >100 % as a coarse ground truth, and the Heating LED shows when the element is actually
   drawing power.
2. **Fit our own probe in the thermowell.** The unit's own probe is pushed into a copper
   pocket, 710 mm deep on the 9E. A second probe there would read the PCM temperature
   directly, turning the anchors into a measurement instead of an inference. This is the
   improvement that would make the estimate good.
3. **Ask Flamco about an undocumented serial header** on the PCB, which is built by
   Sunamp, whose later products do have communication.

Wiring the charge enable input to control would also stop the element from charging
against our wishes.

## Sources

- Flamco product sheet 18202, FlexTherm Eco 9E, 2023/05/03
- [Installatie- en bedieningshandleiding, art.nr 18200, 2022-03 NLD](https://flamco.aalberts-hfc.com/media/files/manuals/Man_FlexTherm_Eco_art.nr18200_2022-03_NLD.pdf)
- [QSG Temperatuursensoren v1.0](https://flamco.aalberts-hfc.com/media/files/manuals/QSG-electronic_FlexTherm_Eco_nld_v1.0.pdf)
- [QSG A2.ET Control Unit Replacement, 2020-10](https://flamco.aalberts-hfc.com/media/files/manuals/QSG_FlexTherm_Eco_Control_Unit_Replacement_2020-10.pdf)
