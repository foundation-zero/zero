# Fahrenheit

The Fahrenheit mimic is the adsorption chiller unit: a card with a yard tag, title and mode badge, the high, medium and low temperature circuit pipes, and the heat pipes between them.

<script setup lang="ts">
import { Fahrenheit } from '../../src/modules/thrapp/mimics/components/fahrenheit'
import { ModeBadge, ModeBadgeMode, ModeBadgeSize } from '../../src/modules/thrapp/mimics/components/mode-badge'
import { YardTag } from '../../src/modules/thrapp/mimics/components/yard-tag'
</script>

## Overview

`Fahrenheit` renders a $296 \times 505$ SVG card. It owns the shell, the state-coloured border, the three circuit loops and the two heat pipes. The yard tag, title and badge are HTML content passed through named slots.

Everything that shows a reading is not part of the component. Pumps, circuit labels (`CircuitLabelInstance`) and the Tin/Tout labels (`PortTemperatureLabelInstance`) are passed through the default slot, which renders inside the component's SVG, so their `x` and `y` are in the unit's own coordinates.

## Props

| Prop | Type | Default | Description |
| --- | --- | --- | --- |
| `state` | `MimicComponentState` | `Normal` | Sets the card-border state colour. |

## Slots

| Slot | Content |
| --- | --- |
| `tag` | Yard tag, top left. |
| `title` | Unit name, centred at the top. |
| `badge` | Mode badge below the title. |
| default | SVG children in the unit's coordinates: pumps and labels. |

<div class="my-6 overflow-x-auto bg-muted p-4">
  <svg viewBox="0 0 296 505" width="296" height="505">
    <Fahrenheit>
      <template #tag><YardTag>1034</YardTag></template>
      <template #title>Fahrenheit</template>
      <template #badge>
        <ModeBadge :mode="ModeBadgeMode.Cooling" label="Cooling" :size="ModeBadgeSize.Asset" />
      </template>
    </Fahrenheit>
  </svg>
</div>

```vue
<FahrenheitInstance
  x="782"
  y="49"
  v-bind="chillers['1034']"
>
  <CircuitLabelInstance
    x="66"
    y="107"
    :title="t('thrapp.mimics.adsorption.chiller.circuits.highTemperature')"
    :heat-transfer="sensors.highTemperature"
  />
  <PortTemperatureLabelInstance
    x="241.34"
    y="94.51"
    port="out"
    field="temperatureReturn"
    :temperature="sensors.highTemperature"
  />
</FahrenheitInstance>
```

## Port temperature labels

`PortTemperatureLabelInstance` shows the temperature where a circuit leaves (`port="out"`) or enters (`port="in"`) the unit. Set `side` to the unit edge the label sits on: the arrow points out of the unit for the outgoing temperature and into it for the incoming one, and is drawn on the outer side of the text.
