<script setup lang="ts">
import { computed } from "vue";
import { BranchFields } from "../dc-converter-pair.types";
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContext } from "../../../data";
import { FlowSensorInstance } from "../../../instances";
import FlowLabelInstance from "../../../instances/FlowLabelInstance.vue";

const props = defineProps<{ fields: BranchFields<MimicComponentType.FlowSensor> }>();

const getContext = getTooltipContext(MimicComponentType.FlowSensor);
// Not `map(getContext)`: map passes the index, which getContext takes as `arrayIndexIfMultiple`.
const flowSensors = computed(() => props.fields.map((field) => getContext(field)));
</script>

<template>
  <g>
    <!-- The source icon is inset in its 40px instance viewBox. -->
    <FlowSensorInstance
      x="547"
      y="126"
      v-bind="flowSensors[0]"
    >
      <FlowLabelInstance
        x="472"
        y="107.5"
        :tag-id="flowSensors[0].tooltip?.yardTag"
        :flow="flowSensors[0].source"
      />
    </FlowSensorInstance>
    <!-- The source icon is inset in its 40px instance viewBox. -->
    <FlowSensorInstance
      x="547"
      y="340"
      v-bind="flowSensors[1]"
    >
      <FlowLabelInstance
        x="472"
        y="321.5"
        :tag-id="flowSensors[1].tooltip?.yardTag"
        :flow="flowSensors[1].source"
      />
    </FlowSensorInstance>
  </g>
</template>
