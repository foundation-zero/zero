<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { getTooltipContexts } from "../../../data";
import { FlowSensorInstance } from "../../../instances";
import FlowLabelInstance from "../../../instances/FlowLabelInstance.vue";

const flowSensors = getTooltipContexts(MimicComponentType.FlowSensor, ["1057-08", "1057-09"]);
</script>

<template>
  <g>
    <!-- The source icon is inset in its 40px instance viewBox. -->
    <FlowSensorInstance
      x="547"
      y="126"
      v-bind="flowSensors['1057-08']"
    >
      <FlowLabelInstance
        x="472"
        y="114"
        :tag-id="flowSensors['1057-08'].tooltip?.yardTag"
        :flow="flowSensors['1057-08'].source"
      />
    </FlowSensorInstance>
    <!-- The source icon is inset in its 40px instance viewBox. -->
    <FlowSensorInstance
      x="547"
      y="340"
      v-bind="flowSensors['1057-09']"
    >
      <FlowLabelInstance
        x="472"
        y="328"
        :tag-id="flowSensors['1057-09'].tooltip?.yardTag"
        :flow="flowSensors['1057-09'].source"
      />
    </FlowSensorInstance>
  </g>
</template>
