<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import { FlowSensorInstance } from "../../../instances";
import FlowLabelInstance from "../../../instances/FlowLabelInstance.vue";

const flowSensors = getTooltipContexts(MimicComponentType.FlowSensor, [
  "1057-04",
  "1057-05",
  "1057-06",
  "1057-07",
]);
</script>

<template>
  <g>
    <!-- The source icon is inset in its 40px instance viewBox. -->
    <FlowSensorInstance
      x="547"
      y="126"
      v-bind="flowSensors['1057-04']"
    >
      <FlowLabelInstance
        x="472"
        y="114"
        :tag-id="flowSensors['1057-04'].tooltip?.yardTag"
        :flow="flowSensors['1057-04'].source"
      />
    </FlowSensorInstance>
    <!-- The source icon is inset in its 40px instance viewBox. -->
    <FlowSensorInstance
      x="547"
      y="340"
      v-bind="flowSensors['1057-05']"
    >
      <FlowLabelInstance
        x="472"
        y="328"
        :tag-id="flowSensors['1057-05'].tooltip?.yardTag"
        :flow="flowSensors['1057-05'].source"
      />
    </FlowSensorInstance>
    <!-- The source icon is inset in its 40px instance viewBox. -->
    <FlowSensorInstance
      x="547"
      y="548"
      v-bind="flowSensors['1057-06']"
    >
      <FlowLabelInstance
        x="472"
        y="534"
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
        y="733"
        :tag-id="flowSensors['1057-07'].tooltip?.yardTag"
        :flow="flowSensors['1057-07'].source"
      />
    </FlowSensorInstance>
  </g>
</template>
