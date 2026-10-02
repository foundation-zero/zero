<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { FLOW_SENSOR_WIDTH } from "../../../components/flow-sensor";
import { FlowSensorInstance } from "../../../instances";
import FlowLabelInstance from "../../../instances/FlowLabelInstance.vue";
import { DC_FLOW_SENSOR_DATA } from "../data";

const flowSensors = DC_FLOW_SENSOR_DATA[MimicComponentType.FlowSensor];
</script>

<template>
  <FlowSensorInstance
    x="692.25"
    y="70"
    :orientation="ComponentOrientation.Down"
    v-bind="flowSensors['1057-25']"
  >
    <FlowLabelInstance
      target-x="692.25"
      :target-width="FLOW_SENSOR_WIDTH"
      y="31.1458"
      :tag-id="flowSensors['1057-25'].tooltip?.yardTag"
      :flow="flowSensors['1057-25'].source"
    />
  </FlowSensorInstance>
  <FlowSensorInstance
    x="692.25"
    y="281.1458"
    :orientation="ComponentOrientation.Down"
    v-bind="flowSensors['1058-06']"
  >
    <FlowLabelInstance
      target-x="692.25"
      :target-width="FLOW_SENSOR_WIDTH"
      y="238.1458"
      :tag-id="flowSensors['1058-06'].tooltip?.yardTag"
      :flow="flowSensors['1058-06'].source"
    />
  </FlowSensorInstance>
  <FlowSensorInstance
    x="692.25"
    y="511.1458"
    :orientation="ComponentOrientation.Down"
    v-bind="flowSensors['1057-26']"
  >
    <FlowLabelInstance
      target-x="692.25"
      :target-width="FLOW_SENSOR_WIDTH"
      y="470.1458"
      :tag-id="flowSensors['1057-26'].tooltip?.yardTag"
      :flow="flowSensors['1057-26'].source"
    />
  </FlowSensorInstance>
  <FlowSensorInstance
    x="1151.1406"
    y="282.1458"
    :orientation="ComponentOrientation.Down"
    v-bind="flowSensors['1058-04']"
  >
    <FlowLabelInstance
      target-x="1151.1406"
      :target-width="FLOW_SENSOR_WIDTH"
      y="239.1458"
      :tag-id="flowSensors['1058-04'].tooltip?.yardTag"
      :flow="flowSensors['1058-04'].source"
    />
  </FlowSensorInstance>
</template>
