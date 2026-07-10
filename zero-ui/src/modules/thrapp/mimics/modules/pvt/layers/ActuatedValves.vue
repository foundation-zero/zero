<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { SensorComponentType } from "@/modules/thrs/types";
import { ComponentOrientation } from "../../../components";
import { MixValveInstance, SwitchValveInstance } from "../../../instances";
import { getField } from "../../../providers";
import { PVT_MIMIC_DATA } from "../data";

const switchValves = PVT_MIMIC_DATA[MimicComponentType.SwitchValve];
</script>

<template>
  <g>
    <SwitchValveInstance
      x="233"
      y="220"
      :orientation="ComponentOrientation.Right"
      v-bind="switchValves['1067-01']"
    />
    <SwitchValveInstance
      x="233"
      y="391"
      :orientation="ComponentOrientation.Right"
      v-bind="switchValves['1067-02']"
    />
    <SwitchValveInstance
      x="233"
      y="550"
      :orientation="ComponentOrientation.Right"
      v-bind="switchValves['1069-01']"
    />

    <MixValveInstance
      x="804"
      y="221"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'pvt', 'pvtMixMainFwd')"
    />
    <MixValveInstance
      x="804"
      y="392"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'pvt', 'pvtMixMainAft')"
    />
    <MixValveInstance
      x="804"
      y="552"
      :orientation="ComponentOrientation.Right"
      :valve="getField(SensorComponentType.Valve, 'pvt', 'pvtMixOwners')"
    />
    <MixValveInstance
      x="944"
      y="513"
      :orientation="ComponentOrientation.Down"
      :valve="getField(SensorComponentType.Valve, 'pvt', 'pvtMixExchanger')"
    />
  </g>
</template>
