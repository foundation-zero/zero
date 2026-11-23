<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import { FlowSensorInstance } from "../../../instances";
import FlowLabelInstance from "../../../instances/FlowLabelInstance.vue";

const flowSensors = getTooltipContexts(MimicComponentType.FlowSensor, ["1057-11", "1057-12"]);
</script>

<template>
  <g>
    <!-- The source icon is inset in its 40px instance viewBox. -->
    <FlowSensorInstance
      x="547"
      y="126"
      v-bind="flowSensors['1057-11']"
    >
      <FlowLabelInstance
        x="472"
        y="107.5"
        :tag-id="flowSensors['1057-11'].tooltip?.yardTag"
        :flow="flowSensors['1057-11'].source"
      />
    </FlowSensorInstance>
    <!-- The source icon is inset in its 40px instance viewBox. -->
    <FlowSensorInstance
      x="547"
      y="340"
      v-bind="flowSensors['1057-12']"
    >
      <FlowLabelInstance
        x="472"
        y="321.5"
        :tag-id="flowSensors['1057-12'].tooltip?.yardTag"
        :flow="flowSensors['1057-12'].source"
      />
    </FlowSensorInstance>
  </g>
</template>
