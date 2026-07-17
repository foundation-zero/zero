<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { FlowSensorInstance } from "../../../instances";
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
    />
    <FlowSensorInstance
      x="286.512"
      y="282"
      tag-id="1218-02"
      :orientation="ComponentOrientation.Down"
      v-bind="flowSensors['1218-02']"
    />
    <FlowSensorInstance
      x="286.512"
      y="551"
      tag-id="1057-22"
      :orientation="ComponentOrientation.Down"
      v-bind="flowSensors['1057-22']"
    />
  </g>
</template>
