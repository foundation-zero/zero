<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { FLOW_SENSOR_WIDTH } from "../../../components/flow-sensor";
import { FlowSensorInstance } from "../../../instances";
import FlowLabelInstance from "../../../instances/FlowLabelInstance.vue";
import { PVT_MIMIC_DATA } from "../data";

const flowSensors = PVT_MIMIC_DATA[MimicComponentType.FlowSensor];
</script>

<template>
  <g>
    <FlowSensorInstance
      x="694"
      y="82"
      :orientation="ComponentOrientation.Down"
      v-bind="flowSensors['1058-12']"
    >
      <FlowLabelInstance
        :target-x="694"
        :target-width="FLOW_SENSOR_WIDTH"
        y="40"
        :tag-id="flowSensors['1058-12'].tooltip?.yardTag"
        :flow="flowSensors['1058-12'].source"
      />
    </FlowSensorInstance>
    <FlowSensorInstance
      x="694"
      y="290"
      :orientation="ComponentOrientation.Down"
      v-bind="flowSensors['1058-13']"
    >
      <FlowLabelInstance
        :target-x="694"
        :target-width="FLOW_SENSOR_WIDTH"
        y="249"
        :tag-id="flowSensors['1058-13'].tooltip?.yardTag"
        :flow="flowSensors['1058-13'].source"
      />
    </FlowSensorInstance>
    <FlowSensorInstance
      x="694"
      y="499"
      :orientation="ComponentOrientation.Down"
      v-bind="flowSensors['1057-03']"
    >
      <FlowLabelInstance
        :target-x="694"
        :target-width="FLOW_SENSOR_WIDTH"
        y="458"
        :tag-id="flowSensors['1057-03'].tooltip?.yardTag"
        :flow="flowSensors['1057-03'].source"
      />
    </FlowSensorInstance>
  </g>
</template>
