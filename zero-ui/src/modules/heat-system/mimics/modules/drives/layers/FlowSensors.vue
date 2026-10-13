<script setup lang="ts">
import { ComponentOrientation } from "../../../components";
import { FLOW_SENSOR_WIDTH } from "../../../components/flow-sensor";
import { FlowSensorInstance } from "../../../instances";
import FlowLabelInstance from "../../../instances/FlowLabelInstance.vue";
import { DRIVES_FLOW_SENSOR_DATA } from "../data";

const flowSensors = DRIVES_FLOW_SENSOR_DATA.FlowSensor;
</script>

<template>
  <g>
    <FlowSensorInstance
      x="322.6582"
      y="147.8291"
      :orientation="ComponentOrientation.Down"
      v-bind="flowSensors['1057-16']"
    >
      <FlowLabelInstance
        target-x="322.6582"
        :target-width="FLOW_SENSOR_WIDTH"
        y="108.916"
        :tag-id="flowSensors['1057-16'].tooltip?.yardTag"
        :flow="flowSensors['1057-16'].source"
      />
    </FlowSensorInstance>
    <FlowSensorInstance
      x="322.6582"
      y="368.916"
      :orientation="ComponentOrientation.Down"
      v-bind="flowSensors['1057-13']"
    >
      <FlowLabelInstance
        target-x="322.6582"
        :target-width="FLOW_SENSOR_WIDTH"
        y="327.916"
        :tag-id="flowSensors['1057-13'].tooltip?.yardTag"
        :flow="flowSensors['1057-13'].source"
      />
    </FlowSensorInstance>
    <FlowSensorInstance
      x="322.6582"
      y="600.8291"
      :orientation="ComponentOrientation.Down"
      v-bind="flowSensors['1057-14']"
    >
      <FlowLabelInstance
        target-x="322.6582"
        :target-width="FLOW_SENSOR_WIDTH"
        y="561.916"
        :tag-id="flowSensors['1057-14'].tooltip?.yardTag"
        :flow="flowSensors['1057-14'].source"
      />
    </FlowSensorInstance>
    <FlowSensorInstance
      x="322.6582"
      y="808.916"
      :orientation="ComponentOrientation.Down"
      v-bind="flowSensors['1057-15']"
    >
      <FlowLabelInstance
        target-x="322.6582"
        :target-width="FLOW_SENSOR_WIDTH"
        y="771.916"
        :tag-id="flowSensors['1057-15'].tooltip?.yardTag"
        :flow="flowSensors['1057-15'].source"
      />
    </FlowSensorInstance>
    <FlowSensorInstance
      x="936.1582"
      y="254.916"
      :orientation="ComponentOrientation.Left"
      v-bind="flowSensors['1057-10']"
    >
      <FlowLabelInstance
        x="860.1582"
        y="250.916"
        :tag-id="flowSensors['1057-10'].tooltip?.yardTag"
        :flow="flowSensors['1057-10'].source"
      />
    </FlowSensorInstance>
    <FlowSensorInstance
      x="1260.1582"
      y="329"
      :orientation="ComponentOrientation.Down"
      v-bind="flowSensors['1058-03']"
    >
      <FlowLabelInstance
        target-x="1260.1582"
        :target-width="FLOW_SENSOR_WIDTH"
        y="293"
        :tag-id="flowSensors['1058-03'].tooltip?.yardTag"
        :flow="flowSensors['1058-03'].source"
      />
    </FlowSensorInstance>
  </g>
</template>
