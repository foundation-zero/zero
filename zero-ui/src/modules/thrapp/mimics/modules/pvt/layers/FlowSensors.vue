<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { FlowSensorInstance } from "../../../instances";
import { PVT_MIMIC_DATA } from "../data";

const flowSensors = PVT_MIMIC_DATA[MimicComponentType.FlowSensor];
</script>

<template>
  <g>
    <FlowSensorInstance
      x="794"
      y="118"
      tag-id="1058-12"
      :orientation="ComponentOrientation.Down"
      v-bind="flowSensors['1058-12']"
    />
    <FlowSensorInstance
      x="794"
      y="289"
      tag-id="1058-13"
      :orientation="ComponentOrientation.Down"
      v-bind="flowSensors['1058-13']"
    />
    <FlowSensorInstance
      x="794"
      y="448"
      tag-id="1057-03"
      :orientation="ComponentOrientation.Down"
      v-bind="flowSensors['1057-03']"
    />
  </g>
</template>
