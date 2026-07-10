<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components/index.ts";
import { FlowControlValveInstance, SwitchValveInstance } from "../../../instances/index.ts";
import { DHW_MIMIC_DATA } from "../data/index.ts";

const switchValves = DHW_MIMIC_DATA[MimicComponentType.SwitchValve];
const flowControlValves = DHW_MIMIC_DATA[MimicComponentType.FlowControlValve];
</script>

<template>
  <g>
    <SwitchValveInstance
      x="361"
      y="156.2099609375"
      :orientation="ComponentOrientation.Right"
      v-bind="switchValves['1067-11']"
    />
    <SwitchValveInstance
      x="417"
      y="156.2099609375"
      :orientation="ComponentOrientation.Right"
      v-bind="switchValves['1067-12']"
    />
    <SwitchValveInstance
      x="472"
      y="156.2099609375"
      :orientation="ComponentOrientation.Right"
      v-bind="switchValves['1067-14']"
    />
    <SwitchValveInstance
      x="525"
      y="156.2099609375"
      :orientation="ComponentOrientation.Right"
      v-bind="switchValves['1067-13']"
    />
    <SwitchValveInstance
      x="715"
      y="156.2099609375"
      :orientation="ComponentOrientation.Right"
      v-bind="switchValves['1067-07']"
    />
    <SwitchValveInstance
      x="769"
      y="156.2099609375"
      :orientation="ComponentOrientation.Right"
      v-bind="switchValves['1067-08']"
    />
    <SwitchValveInstance
      x="824"
      y="156.2099609375"
      :orientation="ComponentOrientation.Right"
      v-bind="switchValves['1067-10']"
    />
    <SwitchValveInstance
      x="877"
      y="156.2099609375"
      :orientation="ComponentOrientation.Right"
      v-bind="switchValves['1067-09']"
    />
    <SwitchValveInstance
      x="1053"
      y="156.2099609375"
      :orientation="ComponentOrientation.Right"
      v-bind="switchValves['1067-03']"
    />
    <SwitchValveInstance
      x="1107"
      y="156.2099609375"
      :orientation="ComponentOrientation.Right"
      v-bind="switchValves['1067-04']"
    />
    <SwitchValveInstance
      x="1161"
      y="156.2099609375"
      :orientation="ComponentOrientation.Right"
      v-bind="switchValves['1067-06']"
    />
    <SwitchValveInstance
      x="1219"
      y="156.2099609375"
      :orientation="ComponentOrientation.Right"
      v-bind="switchValves['1067-05']"
    />

    <SwitchValveInstance
      x="179.5"
      y="586.2099609375"
      :orientation="ComponentOrientation.Right"
      v-bind="switchValves['1067-17']"
    />
    <SwitchValveInstance
      x="211"
      y="554"
      :orientation="ComponentOrientation.Up"
      v-bind="switchValves['1067-16']"
    />
    <SwitchValveInstance
      x="145"
      y="554"
      :orientation="ComponentOrientation.Up"
      v-bind="switchValves['1067-18']"
    />

    <FlowControlValveInstance
      x="1046"
      y="473.2099609375"
      v-bind="flowControlValves['1064-08']"
      :orientation="ComponentOrientation.Up"
    />

    <FlowControlValveInstance
      x="1046"
      y="635"
      v-bind="flowControlValves['1064-03']"
      :orientation="ComponentOrientation.Up"
    />
  </g>
</template>
