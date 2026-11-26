<script setup lang="ts">
import { computed } from "vue";
import { BranchFields } from "../dc-converter-pair.types";
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContext } from "../../../data";
import { TemperatureSensorInstance } from "../../../instances";
import TemperatureLabelInstance from "../../../instances/TemperatureLabelInstance.vue";

const props = defineProps<{ fields: BranchFields<MimicComponentType.TemperatureSensor> }>();

const getContext = getTooltipContext(MimicComponentType.TemperatureSensor);
// Not `map(getContext)`: map passes the index, which getContext takes as `arrayIndexIfMultiple`.
const temperatureSensors = computed(() => props.fields.map((field) => getContext(field)));
</script>

<template>
  <g>
    <!-- The source icon is inset in its 32px instance viewBox. -->
    <TemperatureSensorInstance
      x="551"
      y="8.25"
      v-bind="temperatureSensors[0]"
    >
      <TemperatureLabelInstance
        x="496"
        y="-6.5"
        :tag-id="temperatureSensors[0].tooltip?.yardTag"
        :temperature="temperatureSensors[0].source"
      />
    </TemperatureSensorInstance>
    <!-- The source icon is inset in its 32px instance viewBox. -->
    <TemperatureSensorInstance
      x="551"
      y="222.25"
      v-bind="temperatureSensors[1]"
    >
      <TemperatureLabelInstance
        x="496"
        y="203.5"
        :tag-id="temperatureSensors[1].tooltip?.yardTag"
        :temperature="temperatureSensors[1].source"
      />
    </TemperatureSensorInstance>
  </g>
</template>
