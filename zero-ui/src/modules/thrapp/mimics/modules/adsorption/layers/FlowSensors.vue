<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { getTooltipContexts } from "../../../data";
import { FlowSensorInstance } from "../../../instances";
import FlowLabelInstance from "../../../instances/FlowLabelInstance.vue";

const flowSensors = getTooltipContexts(MimicComponentType.FlowSensor, [
  "1058-02",
  "1058-09",
  "1059",
  "1058-10",
]);
</script>

<template>
  <g>
    <FlowSensorInstance
      x="1278.03"
      y="227"
      :orientation="ComponentOrientation.Down"
      v-bind="flowSensors['1058-02']"
    >
      <FlowLabelInstance
        x="1270.53"
        y="178.5"
        :tag-id="flowSensors['1058-02'].tooltip?.yardTag"
        :flow="flowSensors['1058-02'].source"
      />
    </FlowSensorInstance>
    <FlowSensorInstance
      x="1472"
      y="228.13"
      :orientation="ComponentOrientation.Down"
      v-bind="flowSensors['1058-09']"
    >
      <FlowLabelInstance
        x="1480"
        y="266.63"
        :tag-id="flowSensors['1058-09'].tooltip?.yardTag"
        :flow="flowSensors['1058-09'].source"
      />
    </FlowSensorInstance>
    <FlowSensorInstance
      x="288"
      y="363"
      :orientation="ComponentOrientation.Down"
      v-bind="flowSensors['1059']"
    >
      <FlowLabelInstance
        x="281"
        y="405.5"
        :tag-id="flowSensors['1059'].tooltip?.yardTag"
        :flow="flowSensors['1059'].source"
      />
    </FlowSensorInstance>
    <FlowSensorInstance
      x="161"
      y="253"
      :orientation="ComponentOrientation.Down"
      v-bind="flowSensors['1058-10']"
    >
      <FlowLabelInstance
        x="156"
        y="207.5"
        :tag-id="flowSensors['1058-10'].tooltip?.yardTag"
        :flow="flowSensors['1058-10'].source"
      />
    </FlowSensorInstance>
  </g>
</template>
