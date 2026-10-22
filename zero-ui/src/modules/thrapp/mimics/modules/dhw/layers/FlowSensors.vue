<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { FLOW_SENSOR_WIDTH } from "../../../components/flow-sensor";
import { getTooltipContexts } from "../../../data";
import { FlowSensorInstance } from "../../../instances";
import FlowLabelInstance from "../../../instances/FlowLabelInstance.vue";

const flowSensors = getTooltipContexts(MimicComponentType.FlowSensor, [
  "1057-17",
  "1057-24",
  "1058-11",
]);
</script>

<template>
  <g>
    <FlowSensorInstance
      x="1100"
      y="457.2099609375"
      v-bind="flowSensors['1057-17']"
      :orientation="ComponentOrientation.Down"
    >
      <FlowLabelInstance
        :target-x="1100"
        :target-width="FLOW_SENSOR_WIDTH"
        y="420"
        :tag-id="flowSensors['1057-17'].tooltip?.yardTag"
        :flow="flowSensors['1057-17'].source"
      />
    </FlowSensorInstance>
    <FlowSensorInstance
      x="1101"
      y="616.2099609375"
      v-bind="flowSensors['1057-24']"
      :orientation="ComponentOrientation.Down"
    >
      <FlowLabelInstance
        :target-x="1101"
        :target-width="FLOW_SENSOR_WIDTH"
        y="579"
        :tag-id="flowSensors['1057-24'].tooltip?.yardTag"
        :flow="flowSensors['1057-24'].source"
      />
    </FlowSensorInstance>
    <FlowSensorInstance
      x="192"
      y="468.2099609375"
      v-bind="flowSensors['1058-11']"
      :orientation="ComponentOrientation.Left"
    >
      <FlowLabelInstance
        x="236"
        y="460"
        :tag-id="flowSensors['1058-11'].tooltip?.yardTag"
        :flow="flowSensors['1058-11'].source"
      />
    </FlowSensorInstance>
  </g>
</template>
