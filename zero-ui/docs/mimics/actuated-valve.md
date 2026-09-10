# Actuated Valve

Composable actuator shell for valve mimics. Instead of selecting a built-in variant, you compose marker and body primitives as slot content.

<script setup lang="ts">
import ActuatedValve from '@/modules/thrapp/mimics/components/actuated-valve/ActuatedValve.vue'
import MixValve from '@/modules/thrapp/mimics/components/actuated-valve/MixValve.vue'
import SwitchValve from '@/modules/thrapp/mimics/components/actuated-valve/SwitchValve.vue'
import ThreeWayValve from '@/modules/thrapp/mimics/components/actuated-valve/ThreeWayValve.vue'
import TwoWayValve from '@/modules/thrapp/mimics/components/actuated-valve/TwoWayValve.vue'
import { ValveLeg, ValvePortName } from '@/modules/thrapp/mimics/components/actuated-valve'
import { ComponentOrientation, MimicComponentState } from '@/modules/thrapp/mimics/components'
</script>

## Overview

`ActuatedValve` now works as a base container that provides:

- orientation and rotation behavior
- mimic state coloring (`normal`, `manual`, `alarm`)
- center pivot and actuator stem

The valve geometry and marker are provided by slot children:

- `TwoWayValve` or `ThreeWayValve` for ports/body
- `SwitchValve` or `MixValve` for actuator marker

This matches how runtime instances are composed in THRAPP:

- switch: `SwitchValve + TwoWayValve`
- flow-control: `MixValve + TwoWayValve`
- three-way switch: `SwitchValve + ThreeWayValve`
- three-way mix: `MixValve + ThreeWayValve`

## Composition Examples

### Switch Valve

<div class="my-6 flex flex-col items-center justify-center gap-2">
  <div class="rounded-md bg-muted p-4">
    <ActuatedValve :state="MimicComponentState.Normal" :rotation="0.35">
      <SwitchValve>A</SwitchValve>
      <TwoWayValve :flow="0.65" />
    </ActuatedValve>
  </div>
  <span class="text-sm font-mono">SwitchValve + TwoWayValve</span>
</div>

```vue
<ActuatedValve :state="MimicComponentState.Normal" :rotation="0.35">
  <SwitchValve>A</SwitchValve>
  <TwoWayValve :flow="0.65" />
</ActuatedValve>
```

### Flow-Control Valve

<div class="my-6 flex flex-col items-center justify-center gap-2">
  <div class="rounded-md bg-muted p-4">
    <ActuatedValve>
      <TwoWayValve :flow="0.45" />
      <MixValve />
    </ActuatedValve>
  </div>
  <span class="text-sm font-mono">MixValve + TwoWayValve</span>
</div>

```vue
<ActuatedValve>
  <TwoWayValve :flow="0.45" />
  <MixValve />
</ActuatedValve>
```

### Three-Way Switch Valve

<div class="my-6 flex flex-col items-center justify-center gap-2">
  <div class="rounded-md bg-muted p-4">
    <ActuatedValve>
      <SwitchValve />
      <ThreeWayValve :flow="0" />
    </ActuatedValve>
  </div>
  <span class="text-sm font-mono">SwitchValve + ThreeWayValve</span>
</div>

```vue
<ActuatedValve>
  <SwitchValve />
  <ThreeWayValve :flow="0" />
</ActuatedValve>
```

### Three-Way Mix Valve

<div class="my-6 flex flex-col items-center justify-center gap-2">
  <div class="rounded-md bg-muted p-4 flex gap-6">
    <ActuatedValve>
      <MixValve />
      <ThreeWayValve :flow="0.7" />
    </ActuatedValve>
    <ActuatedValve :orientation="ComponentOrientation.Right">
      <MixValve />
      <ThreeWayValve :flow="0.7" />
    </ActuatedValve>
    <ActuatedValve :orientation="ComponentOrientation.Down">
      <MixValve />
      <ThreeWayValve :flow="0.7" />
    </ActuatedValve>
  </div>
  <span class="text-sm font-mono">MixValve + ThreeWayValve</span>
</div>

```vue
<ActuatedValve>
  <MixValve />
  <ThreeWayValve :flow="0.7" />
</ActuatedValve>
```

## Orientation and Rotation

- `orientation` rotates the full component relative to `ComponentOrientation.Up`.
- `rotation` is an extra quarter-turn style offset used by instances to reflect actuator position.
- The switch instance pattern uses `:rotation="1 - valve.positionRel"`, so the marker turns opposite to opening ratio.

## Three-Way Leg Labels

`ThreeWayValve` labels its legs with the port names `A`, `B`, and `AB`. Which port sits on which leg is fixed by the schematic, so it is configured up front through the `legs` prop and never derived from flow:

```ts
type ThreeWayValveLegs = Record<ValveLeg, ValvePortName>;

// Default
const THREE_WAY_VALVE_DEFAULT_LEGS = {
  [ValveLeg.Left]: ValvePortName.A,
  [ValveLeg.Right]: ValvePortName.AB,
  [ValveLeg.Bottom]: ValvePortName.B,
};
```

Fill follows the port, not the leg:

- `AB` is the common port and is always 100% filled.
- `A` carries `flow`, `B` carries `1 - flow`.

Label anchors are derived from the leg and the port's text width, so any port can sit on any leg. The anchors rotate with the valve body, but each glyph is counter-rotated by the same angle so the text always reads upright. Anchors sit just outside the 36x36 viewBox, so `ActuatedValve` renders with `overflow-visible`.

`MixValveInstance` passes the raw `positionRel`, so `A` and `B` share the flow between them. `ThreeWaySwitchValveInstance` rounds `positionRel`, so exactly one of `A` or `B` is fully open.

<div class="my-6 flex flex-col items-center justify-center gap-2">
  <div class="rounded-md bg-muted p-4 flex gap-6">
    <ActuatedValve>
      <MixValve />
      <ThreeWayValve :flow="0.7" />
    </ActuatedValve>
    <ActuatedValve>
      <MixValve />
      <ThreeWayValve :flow="0.7" :legs="{ [ValveLeg.Left]: ValvePortName.AB, [ValveLeg.Right]: ValvePortName.B, [ValveLeg.Bottom]: ValvePortName.A }" />
    </ActuatedValve>
  </div>
  <span class="text-sm font-mono">default legs vs. custom legs</span>
</div>

```vue
<ActuatedValve>
  <MixValve />
  <ThreeWayValve
    :flow="0.7"
    :legs="{
      [ValveLeg.Left]: ValvePortName.AB,
      [ValveLeg.Right]: ValvePortName.B,
      [ValveLeg.Bottom]: ValvePortName.A,
    }"
  />
</ActuatedValve>
```

## API

### ActuatedValve Props

| Prop | Type | Default | Description |
|---|---|---|---|
| `orientation` | `ComponentOrientation` | `ComponentOrientation.Up` | Desired orientation in the mimic |
| `rotation` | `Ratio` | `0` | Additional rotational offset for actuator position |
| `state` | `MimicComponentState` | `MimicComponentState.Normal` | State color source (`normal`, `manual`, `alarm`) |

### Slot Primitives

| Component | Props | Description |
|---|---|---|
| `SwitchValve` | default slot text (optional) | Circular marker with optional label (`E` by default) |
| `MixValve` | — | Diagonal arrow marker for flow-control and mixing valves |
| `TwoWayValve` | `flow: Ratio` | Two triangular ports (left/right) with shared flow fill |
| `ThreeWayValve` | `flow: Ratio`, `legs?: ThreeWayValveLegs` | Three-way ports labelled `A` / `B` / `AB`: `A` uses `flow`, `B` uses `1 - flow`, `AB` is fixed open |

## Semantic Token Mapping

| Element | Token |
|---|---|
| Base stroke + state accent (`normal`) | `var(--attention)` |
| Base stroke + state accent (`manual`) | `var(--warning)` |
| Base stroke + state accent (`alarm`) | `var(--destructive)` |
| Port base fill | `var(--attention-dull)` |
| Port active overlay | `var(--attention)` |
| Marker fill | `var(--muted)` |
| Marker text | `var(--foreground)` |
| Leg label knockout | `var(--background)` |
| Leg label text | `var(--foreground)` |

## Notes

- Prefer instance components for production modules (`SwitchValveInstance`, `FlowControlValveInstance`, `MixValveInstance`, `ThreeWaySwitchValveInstance`) because they already wire telemetry (`positionRel`) and `MimicComponentState`.
- Keep composition order consistent with existing instances: marker + body children inside one `ActuatedValve`.
