<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { TemperatureSensorInstance } from "../../../instances";
import { THRUSTERS_MIMIC_DATA } from "../data";

const temperatureSensors = THRUSTERS_MIMIC_DATA[MimicComponentType.TemperatureSensor];
</script>

<template>
  <g>
    <TemperatureSensorInstance
      x="286.512"
      y="145.926"
      tag-id="1038-01"
      :orientation="ComponentOrientation.Right"
      v-bind="temperatureSensors['1038-01']"
    />
    <TemperatureSensorInstance
      x="286.512"
      y="354.354"
      tag-id="1038-02"
      :orientation="ComponentOrientation.Right"
      v-bind="temperatureSensors['1038-02']"
    />
    <TemperatureSensorInstance
      x="837.963"
      y="449.196"
      tag-id="1038-28"
      :orientation="ComponentOrientation.Down"
      v-bind="temperatureSensors['1038-28']"
    />
    <TemperatureSensorInstance
      x="622.797"
      y="270.006"
      tag-id="1038-30"
      :orientation="ComponentOrientation.Down"
      v-bind="temperatureSensors['1038-30']"
    />
  </g>
</template>
