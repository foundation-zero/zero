# PCM

The PCM (phase-change material) mimic is a thermal battery card with title, state badges, power readout, and fixed process-pipe labels.

<script setup lang="ts">
import { RiFireLine, RiTempHotLine } from '@remixicon/vue'
import { ChargeState, ChargingMode, Pcm, PcmChargeState, PcmChargingMode, PcmTitle } from '../../src/modules/thrapp/mimics/components/pcm'
import ValueList from '../../src/modules/thrapp/mimics/components/value-list/ValueList.vue'
import ValueListItem from '../../src/modules/thrapp/mimics/components/value-list/ValueListItem.vue'
import ValueListSeparator from '../../src/modules/thrapp/mimics/components/value-list/ValueListSeparator.vue'
import { YardTag } from '../../src/modules/thrapp/mimics/components/yard-tag'
</script>

## Overview

`Pcm` renders a $260 \times 180$ SVG card. It owns the shell, state-coloured border, process-pipe geometry, and connection labels. Compose `YardTag`, `PcmTitle`, `PcmChargingMode`, `PcmChargeState`, and measurement components inside its default slot.

The connection labels are always present: **B**, **A**, **D**, and **C**. This deliberately includes **A** and **D** in the diagonal layout, where the supplied Figma example did not display them.

## Props

| Prop | Type | Default | Description |
| --- | --- | --- | --- |
| `layout` | `PcmLayout` | `LeftTopBottom` | Selects the pipe layout and content padding. |
| `state` | `MimicComponentState` | `Normal` | Sets the card-border state color. |

## Composition

The single default slot is a regular HTML flex column. Place the identifier first, followed by `PcmTitle`, then `PcmChargingMode`, `PcmChargeState`, and readouts. The title has the normal left inset and extends through the standard right inset.

<div class="my-6 overflow-x-auto bg-muted p-4">
  <Pcm>
    <YardTag>1049</YardTag>
    <PcmTitle>Heat battery</PcmTitle>
    <PcmChargingMode :mode="ChargingMode.Charging">Charging</PcmChargingMode>
    <PcmChargeState :state="ChargeState.Full">Full</PcmChargeState>
    <ValueList class="mt-2 gap-0 text-base font-medium">
      <ValueListSeparator />
      <ValueListItem>
        <RiFireLine class="text-heating-medium size-3.5" />
        <span>+5 kW</span>
      </ValueListItem>
      <ValueListItem>
        <RiTempHotLine class="text-muted-foreground size-3.5" />
        <span>est. 250 kWh</span>
      </ValueListItem>
      <ValueListSeparator />
    </ValueList>
  </Pcm>
</div>

```vue
<script setup lang="ts">
import { RiFireLine, RiTempHotLine } from "@remixicon/vue";
import { ChargeState, ChargingMode, Pcm, PcmChargeState, PcmChargingMode, PcmLayout, PcmTitle } from "@/modules/thrapp/mimics/components/pcm";
import { ValueList, ValueListItem, ValueListSeparator } from "@/modules/thrapp/mimics/components/value-list";
import { YardTag } from "@/modules/thrapp/mimics/components/yard-tag";
</script>

<template>
  <Pcm :layout="PcmLayout.LeftTopBottom">
    <YardTag>1049</YardTag>
    <PcmTitle>Heat battery</PcmTitle>
    <PcmChargingMode :mode="ChargingMode.Charging">Charging</PcmChargingMode>
    <PcmChargeState :state="ChargeState.Full">Full</PcmChargeState>
    <ValueList class="mt-2 gap-0 text-base font-medium">
      <ValueListSeparator />
      <ValueListItem>
        <RiFireLine class="text-heating-medium size-3.5" />
        <span>+5 kW</span>
      </ValueListItem>
      <ValueListItem>
        <RiTempHotLine class="text-muted-foreground size-3.5" />
        <span>est. 250 kWh</span>
      </ValueListItem>
      <ValueListSeparator />
    </ValueList>
  </Pcm>
</template>
```

## Layouts

### Left, Top, and Bottom

`PcmLayout.LeftTopBottom` is the standard layout. Its content uses a $16$ px right inset, with both pipes on the left edge of the card.

### Diagonal

`PcmLayout.LeftRight` supports the top-left and bottom-right pipe arrangement. Its content reserves a $50$ px right inset to clear the lower-right pipe, while the title remains full-width.

```vue
<Pcm :layout="PcmLayout.LeftRight">
  <YardTag>1050</YardTag>
  <PcmTitle>Heat battery</PcmTitle>
  <PcmChargingMode :mode="ChargingMode.Charging">Charging</PcmChargingMode>
  <PcmChargeState :state="ChargeState.Full">Full</PcmChargeState>
  <ValueList><!-- Pcm applies the extra right-side inset. --></ValueList>
</Pcm>
```

## Instance Usage

Use `PcmInstance` in a mimic layer when the card needs the standard tooltip integration. Pass display values as strings until PCM-specific source fields are available.

```vue
<PcmInstance
  :layout="PcmLayout.LeftRight"
  :tooltip="{ title: 'Heat battery 1', yardTag: '1049' }"
  charging-label="Charging"
  fill-label="Full"
  heat-power="+5 kW"
  stored-energy="est. 250 kWh"
/>
```

## Tokens

| Role | Token |
| --- | --- |
| Card surface | `background` |
| Pipe strokes | `flows-pipe` |
| Labels and readouts | `foreground` |
| Normal, manual, and alarm border | State mapping from `MimicComponent` |
| Charging badge | `constructive` |
| Full badge and heat icon | `heating-high` |