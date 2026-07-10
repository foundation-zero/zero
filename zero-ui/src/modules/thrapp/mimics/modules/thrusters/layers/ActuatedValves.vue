<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrs/types";
import { ComponentOrientation } from "../../../components";
import { MixValveInstance, SwitchValveInstance } from "../../../instances";
import { getField } from "../../../providers";
import { THRUSTERS_MIMIC_DATA } from "../data";

const switchValves = THRUSTERS_MIMIC_DATA[MimicComponentType.SwitchValve];
</script>

<template>
  <g>
    <SwitchValveInstance
      x="407"
      y="156"
      :orientation="ComponentOrientation.Right"
      v-bind="switchValves['1091-01']"
    />
    <SwitchValveInstance
      x="407"
      y="364"
      :orientation="ComponentOrientation.Right"
      v-bind="switchValves['1091-02']"
    />
    <SwitchValveInstance
      x="565"
      y="280"
      :orientation="ComponentOrientation.Right"
      v-bind="switchValves['1066-03']"
    />

    <MixValveInstance
      x="214"
      y="418"
      :orientation="ComponentOrientation.Up"
      :valve="getField(SensorComponentType.Valve, 'thrusters', 'thrustersFlowcontrolFwd')"
    />
    <MixValveInstance
      x="214"
      y="159"
      :orientation="ComponentOrientation.Up"
      :valve="getField(SensorComponentType.Valve, 'thrusters', 'thrustersFlowcontrolAft')"
    />

    <MixValveInstance
      x="748"
      y="199"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'thrusters', 'thrustersMixExchanger')"
    />
    <MixValveInstance
      x="683"
      y="283"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'thrusters', 'thrustersMixRecovery')"
    />
  </g>
</template>
