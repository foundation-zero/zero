<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { TemperatureSensorInstance } from "../../../instances";
import { PVT_MIMIC_DATA } from "../data";

const temperatureSensors = PVT_MIMIC_DATA[MimicComponentType.TemperatureSensor];
</script>

<template>
  <g>
    <TemperatureSensorInstance
      x="298"
      y="84"
      tag-id="1038-03"
      :orientation="ComponentOrientation.Right"
      v-bind="temperatureSensors['1038-03']"
    />
    <TemperatureSensorInstance
      x="298"
      y="255"
      tag-id="1038-73"
      :orientation="ComponentOrientation.Right"
      v-bind="temperatureSensors['1038-73']"
    />
    <TemperatureSensorInstance
      x="298"
      y="425"
      tag-id="1038-04"
      :orientation="ComponentOrientation.Right"
      v-bind="temperatureSensors['1038-04']"
    />
    <TemperatureSensorInstance
      x="468"
      y="338"
      tag-id="1038-22"
      :orientation="ComponentOrientation.Down"
      v-bind="temperatureSensors['1038-22']"
    />
    <TemperatureSensorInstance
      x="468"
      y="509"
      tag-id="1038-21"
      :orientation="ComponentOrientation.Down"
      v-bind="temperatureSensors['1038-21']"
    />
    <TemperatureSensorInstance
      x="960"
      y="593"
      tag-id="1038-24"
      :orientation="ComponentOrientation.Right"
      v-bind="temperatureSensors['1038-24']"
    />
  </g>
</template>
