<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { FlowSensorInstance } from "../../../instances";
import { BOILERS_MIMIC_DATA } from "../data";

const flowSensors = BOILERS_MIMIC_DATA[MimicComponentType.FlowSensor];
</script>

<template>
  <g>
    <FlowSensorInstance
      x="1100"
      y="457.2099609375"
      tag-id="1057-24"
      v-bind="flowSensors['1057-24']"
      :orientation="ComponentOrientation.Down"
    />
    <FlowSensorInstance
      x="1101"
      y="616.2099609375"
      tag-id="1057-17"
      v-bind="flowSensors['1057-17']"
      :orientation="ComponentOrientation.Down"
    />
    <FlowSensorInstance
      x="192"
      y="468.2099609375"
      tag-id="1058-11"
      v-bind="flowSensors['1058-11']"
      :orientation="ComponentOrientation.Left"
    />
  </g>
</template>
