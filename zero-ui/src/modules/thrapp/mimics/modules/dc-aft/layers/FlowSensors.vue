<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import { FlowSensorInstance } from "../../../instances";
import FlowLabelInstance from "../../../instances/FlowLabelInstance.vue";

const flowSensors = getTooltipContexts(MimicComponentType.FlowSensor, ["1057-06", "1057-07"]);
</script>

<template>
  <g>
    <!-- The source icon is inset in its 40px instance viewBox. -->
    <FlowSensorInstance
      x="547"
      y="548"
      v-bind="flowSensors['1057-06']"
    >
      <FlowLabelInstance
        x="472"
        y="527.5"
        :tag-id="flowSensors['1057-06'].tooltip?.yardTag"
        :flow="flowSensors['1057-06'].source"
      />
    </FlowSensorInstance>
    <!-- The source icon is inset in its 40px instance viewBox. -->
    <FlowSensorInstance
      x="547"
      y="742"
      v-bind="flowSensors['1057-07']"
    >
      <FlowLabelInstance
        x="472"
        y="726.5"
        :tag-id="flowSensors['1057-07'].tooltip?.yardTag"
        :flow="flowSensors['1057-07'].source"
      />
    </FlowSensorInstance>
  </g>
</template>
