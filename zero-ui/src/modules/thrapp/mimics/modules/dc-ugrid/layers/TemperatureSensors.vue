<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import { TemperatureSensorInstance } from "../../../instances";
import TemperatureLabelInstance from "../../../instances/TemperatureLabelInstance.vue";

const temperatureSensors = getTooltipContexts(MimicComponentType.TemperatureSensor, [
  "1038-09",
  "1038-10",
]);
</script>

<template>
  <g>
    <!-- The source icon is inset in its 32px instance viewBox. -->
    <TemperatureSensorInstance
      x="551"
      y="8.25"
      v-bind="temperatureSensors['1038-09']"
    >
      <TemperatureLabelInstance
        x="496"
        y="-6.5"
        :tag-id="temperatureSensors['1038-09'].tooltip?.yardTag"
        :temperature="temperatureSensors['1038-09'].source"
      />
    </TemperatureSensorInstance>
    <!-- The source icon is inset in its 32px instance viewBox. -->
    <TemperatureSensorInstance
      x="551"
      y="222.25"
      v-bind="temperatureSensors['1038-10']"
    >
      <TemperatureLabelInstance
        x="496"
        y="203.5"
        :tag-id="temperatureSensors['1038-10'].tooltip?.yardTag"
        :temperature="temperatureSensors['1038-10'].source"
      />
    </TemperatureSensorInstance>
  </g>
</template>
