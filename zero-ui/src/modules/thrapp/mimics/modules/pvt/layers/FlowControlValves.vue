<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { FlowControlValveInstance } from "../../../instances";
import { PVT_MIMIC_DATA } from "../data";

const valves = PVT_MIMIC_DATA[MimicComponentType.FlowControlValve];
</script>

<template>
  <g>
    <FlowControlValveInstance
      x="624"
      y="225"
      tag-id="1018"
      :orientation="ComponentOrientation.Right"
      v-bind="valves['1018']"
    />
    <FlowControlValveInstance
      x="624"
      y="367"
      tag-id="1019"
      :orientation="ComponentOrientation.Right"
      v-bind="valves['1019']"
    />
    <FlowControlValveInstance
      x="624"
      y="565"
      tag-id="1021"
      :orientation="ComponentOrientation.Right"
      v-bind="valves['1021']"
    />
  </g>
</template>
