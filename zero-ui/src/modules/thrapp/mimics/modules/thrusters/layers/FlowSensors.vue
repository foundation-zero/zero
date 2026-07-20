<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
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
      tag-id="1218-01"
      :orientation="ComponentOrientation.Down"
      v-bind="flowSensors['1218-01']"
    >
      <FlowLabelInstance
        x="836"
        y="386"
        tag-id="1218-01"
        :flow="flowSensors['1218-01'].source"
      />
    </FlowSensorInstance>
    <FlowSensorInstance
      x="286.512"
      y="282"
      tag-id="1218-02"
      :orientation="ComponentOrientation.Down"
      v-bind="flowSensors['1218-02']"
    >
      <FlowLabelInstance
        x="280"
        y="243"
        tag-id="1218-02"
        :flow="flowSensors['1218-02'].source"
      />
    </FlowSensorInstance>
    <FlowSensorInstance
      x="286.512"
      y="551"
      tag-id="1057-22"
      :orientation="ComponentOrientation.Down"
      v-bind="flowSensors['1057-22']"
    >
      <FlowLabelInstance
        x="280"
        y="513"
        tag-id="1057-22"
        :flow="flowSensors['1057-22'].source"
      />
    </FlowSensorInstance>
  </g>
</template>
