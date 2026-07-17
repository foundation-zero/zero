<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PressureSensorInstance } from "../../../instances";
import { THRUSTERS_MIMIC_DATA } from "../data";

const pressureSensors = THRUSTERS_MIMIC_DATA[MimicComponentType.PressureSensor];
</script>

<template>
  <g>
    <PressureSensorInstance
      x="465.441"
      y="555"
      :orientation="ComponentOrientation.Down"
      v-bind="pressureSensors['1097-01']"
    />
    <PressureSensorInstance
      x="938.637"
      y="229"
      :orientation="ComponentOrientation.Down"
      v-bind="pressureSensors['1097-02']"
    />
  </g>
</template>
