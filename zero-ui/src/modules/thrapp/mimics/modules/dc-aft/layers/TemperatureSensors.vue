<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import { TemperatureSensorInstance } from "../../../instances";
import TemperatureLabelInstance from "../../../instances/TemperatureLabelInstance.vue";

const temperatureSensors = getTooltipContexts(MimicComponentType.TemperatureSensor, [
  "1038-07",
  "1038-08",
]);
</script>

<template>
  <g>
    <!-- The source icon is inset in its 32px instance viewBox. -->
    <TemperatureSensorInstance
      x="551"
      y="429.25"
      v-bind="temperatureSensors['1038-07']"
    >
      <TemperatureLabelInstance
        x="496"
        y="409.5"
        :tag-id="temperatureSensors['1038-07'].tooltip?.yardTag"
        :temperature="temperatureSensors['1038-07'].source"
      />
    </TemperatureSensorInstance>
    <!-- The source icon is inset in its 32px instance viewBox. -->
    <TemperatureSensorInstance
      x="551"
      y="624.25"
      v-bind="temperatureSensors['1038-08']"
    >
      <TemperatureLabelInstance
        x="496"
        y="601.5"
        :tag-id="temperatureSensors['1038-08'].tooltip?.yardTag"
        :temperature="temperatureSensors['1038-08'].source"
      />
    </TemperatureSensorInstance>
  </g>
</template>
