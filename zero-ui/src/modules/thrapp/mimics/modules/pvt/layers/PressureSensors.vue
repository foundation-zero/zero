<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PressureSensorInstance } from "../../../instances";
import { PVT_MIMIC_DATA } from "../data";

const pressureSensors = PVT_MIMIC_DATA[MimicComponentType.PressureSensor];
</script>

<template>
  <g>
    <PressureSensorInstance
      x="705"
      y="171"
      :orientation="ComponentOrientation.Down"
      v-bind="pressureSensors['1097-03']"
    />
    <PressureSensorInstance
      x="705"
      y="341"
      :orientation="ComponentOrientation.Down"
      v-bind="pressureSensors['1097-04']"
    />
    <PressureSensorInstance
      x="705"
      y="511"
      :orientation="ComponentOrientation.Down"
      v-bind="pressureSensors['1097-05']"
    />
    <PressureSensorInstance
      x="946"
      y="259"
      :orientation="ComponentOrientation.Right"
      v-bind="pressureSensors['1097-06']"
    />
  </g>
</template>
