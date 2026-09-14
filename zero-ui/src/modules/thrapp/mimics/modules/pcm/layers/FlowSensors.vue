<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { FLOW_SENSOR_WIDTH } from "../../../components/flow-sensor";
import { FlowSensorInstance } from "../../../instances";
import FlowLabelInstance from "../../../instances/FlowLabelInstance.vue";
import { PCM_MIMIC_DATA } from "../data";

const flowSensors = PCM_MIMIC_DATA[MimicComponentType.FlowSensor];
</script>

<template>
  <FlowSensorInstance
    x="460"
    y="54"
    :orientation="ComponentOrientation.Down"
    v-bind="flowSensors['1057-18']"
  >
    <FlowLabelInstance
      y="15"
      :target-x="460"
      :target-width="FLOW_SENSOR_WIDTH"
      :tag-id="flowSensors['1057-18'].tooltip?.yardTag"
      :flow="flowSensors['1057-18'].source"
    />
  </FlowSensorInstance>
  <FlowSensorInstance
    x="460"
    y="203"
    :orientation="ComponentOrientation.Down"
    v-bind="flowSensors['1057-19']"
  >
    <FlowLabelInstance
      y="250"
      :target-x="460"
      :target-width="FLOW_SENSOR_WIDTH"
      :tag-id="flowSensors['1057-19'].tooltip?.yardTag"
      :flow="flowSensors['1057-19'].source"
    />
  </FlowSensorInstance>
  <FlowSensorInstance
    x="460"
    y="399"
    :orientation="ComponentOrientation.Down"
    v-bind="flowSensors['1057-20']"
  >
    <FlowLabelInstance
      y="449"
      :target-x="460"
      :target-width="FLOW_SENSOR_WIDTH"
      :tag-id="flowSensors['1057-20'].tooltip?.yardTag"
      :flow="flowSensors['1057-20'].source"
    />
  </FlowSensorInstance>
  <FlowSensorInstance
    x="460"
    y="597"
    :orientation="ComponentOrientation.Down"
    v-bind="flowSensors['1057-21']"
  >
    <FlowLabelInstance
      y="646"
      :target-x="460"
      :target-width="FLOW_SENSOR_WIDTH"
      :tag-id="flowSensors['1057-21'].tooltip?.yardTag"
      :flow="flowSensors['1057-21'].source"
    />
  </FlowSensorInstance>
  <FlowSensorInstance
    x="1100"
    y="715"
    :orientation="ComponentOrientation.Right"
    v-bind="flowSensors['1058-07-1']"
  >
    <FlowLabelInstance
      target-x="1100"
      y="710"
      :tag-id="flowSensors['1058-07-1'].tooltip?.yardTag"
      :flow="flowSensors['1058-07-1'].source"
    />
  </FlowSensorInstance>
  <FlowSensorInstance
    x="1224"
    y="715"
    :orientation="ComponentOrientation.Right"
    v-bind="flowSensors['1058-07-2']"
  >
    <FlowLabelInstance
      target-x="1224"
      y="710"
      :tag-id="flowSensors['1058-07-2'].tooltip?.yardTag"
      :flow="flowSensors['1058-07-2'].source"
    />
  </FlowSensorInstance>
  <FlowSensorInstance
    x="1348"
    y="715"
    :orientation="ComponentOrientation.Right"
    v-bind="flowSensors['1192']"
  >
    <FlowLabelInstance
      target-x="1348"
      y="710"
      :tag-id="flowSensors['1192'].tooltip?.yardTag"
      :flow="flowSensors['1192'].source"
    />
  </FlowSensorInstance>
</template>
