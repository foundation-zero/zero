<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { MixValveInstance, SwitchValveInstance } from "../../../instances";
import FlowControlValveInstance from "../../../instances/FlowControlValveInstance.vue";
import { THRUSTERS_MIMIC_DATA } from "../data";

const switchValves = THRUSTERS_MIMIC_DATA[MimicComponentType.SwitchValve];
const flowControlValves = THRUSTERS_MIMIC_DATA[MimicComponentType.FlowControlValve];
const mixValves = THRUSTERS_MIMIC_DATA[MimicComponentType.MixValve];
</script>

<template>
  <g>
    <MixValveInstance
      x="414"
      y="193"
      :orientation="ComponentOrientation.Up"
      v-bind="mixValves['1091-01']"
    />
    <MixValveInstance
      x="414"
      y="449.5"
      :orientation="ComponentOrientation.Down"
      v-bind="mixValves['1091-02']"
    />
    <SwitchValveInstance
      x="575"
      y="346"
      :orientation="ComponentOrientation.Up"
      v-bind="switchValves['1066-03']"
    />

    <FlowControlValveInstance
      x="214"
      y="193"
      :orientation="ComponentOrientation.Up"
      v-bind="flowControlValves['1215']"
    />
    <FlowControlValveInstance
      x="214"
      y="449"
      :orientation="ComponentOrientation.Up"
      v-bind="flowControlValves['1064-02']"
    />

    <MixValveInstance
      x="759.5"
      y="242"
      :orientation="ComponentOrientation.Down"
      v-bind="mixValves['1214-01']"
    />
    <MixValveInstance
      x="693.5"
      y="346"
      :orientation="ComponentOrientation.Up"
      v-bind="mixValves['1074']"
    />
  </g>
</template>
