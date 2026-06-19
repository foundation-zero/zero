<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PressureSensorInstance } from "../../../instances";
import { BOILERS_MIMIC_DATA } from "../data";

const pressureSensors = BOILERS_MIMIC_DATA[MimicComponentType.PressureSensor];
</script>

<template>
  <g>
    <PressureSensorInstance
      x="559"
      y="109.2099609375"
      tag-id="1056-01"
      v-bind="pressureSensors['1056-01']"
      :orientation="ComponentOrientation.Left"
    />
    <PressureSensorInstance
      x="921"
      y="109.2099609375"
      tag-id="1056-02"
      v-bind="pressureSensors['1056-02']"
      :orientation="ComponentOrientation.Left"
    />
    <PressureSensorInstance
      x="1260"
      y="109.2099609375"
      tag-id="1056-03"
      v-bind="pressureSensors['1056-03']"
      :orientation="ComponentOrientation.Left"
    />
    <PressureSensorInstance
      x="289"
      y="221.2099609375"
      tag-id="1097-11"
      v-bind="pressureSensors['1097-11']"
      :orientation="ComponentOrientation.Down"
    />
  </g>
</template>
