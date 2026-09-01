<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { FLOW_SENSOR_WIDTH } from "../../../components/flow-sensor";
import { FlowSensorInstance } from "../../../instances";
import FlowLabelInstance from "../../../instances/FlowLabelInstance.vue";
import { THRUSTERS_MIMIC_DATA } from "../data";

const flowSensors = THRUSTERS_MIMIC_DATA[MimicComponentType.FlowSensor];
</script>

<template>
  <g>
    <FlowSensorInstance
      x="837.963"
      y="432"
      :orientation="ComponentOrientation.Down"
      v-bind="flowSensors['1218-01']"
    >
      <FlowLabelInstance
        :target-x="837.963"
        :target-width="FLOW_SENSOR_WIDTH"
        y="386"
        :tag-id="flowSensors['1218-01'].tooltip?.yardTag"
        :flow="flowSensors['1218-01'].source"
      />
    </FlowSensorInstance>
    <FlowSensorInstance
      x="280"
      y="282"
      :orientation="ComponentOrientation.Down"
      v-bind="flowSensors['1218-02']"
    >
      <FlowLabelInstance
        x="320"
        y="268"
        :tag-id="flowSensors['1218-02'].tooltip?.yardTag"
        :flow="flowSensors['1218-02'].source"
      />
    </FlowSensorInstance>
    <FlowSensorInstance
      x="280"
      y="551"
      :orientation="ComponentOrientation.Down"
      v-bind="flowSensors['1057-22']"
    >
      <FlowLabelInstance
        x="320"
        y="535"
        :tag-id="flowSensors['1057-22'].tooltip?.yardTag"
        :flow="flowSensors['1057-22'].source"
      />
    </FlowSensorInstance>
  </g>
</template>
