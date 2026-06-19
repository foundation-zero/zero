<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { TemperatureSensorInstance } from "../../../instances";
import { DHW_MIMIC_DATA } from "../data";

const temperatureSensors = DHW_MIMIC_DATA[MimicComponentType.TemperatureSensor];
</script>

<template>
  <g>
    <TemperatureSensorInstance
      x="324"
      y="109.2099609375"
      tag-id="1038-45"
      v-bind="temperatureSensors['1038-45']"
      :orientation="ComponentOrientation.Right"
    />
    <TemperatureSensorInstance
      x="687"
      y="109.2099609375"
      tag-id="1038-44"
      v-bind="temperatureSensors['1038-44']"
      :orientation="ComponentOrientation.Right"
    />
    <TemperatureSensorInstance
      x="1025"
      y="109.2099609375"
      tag-id="1038-27"
      v-bind="temperatureSensors['1038-27']"
      :orientation="ComponentOrientation.Right"
    />
    <TemperatureSensorInstance
      x="185"
      y="196.2099609375"
      tag-id="1038-65"
      v-bind="temperatureSensors['1038-65']"
      :orientation="ComponentOrientation.Down"
    />
    <TemperatureSensorInstance
      x="1170"
      y="534"
      tag-id="1038-47"
      v-bind="temperatureSensors['1038-47']"
      :orientation="ComponentOrientation.Down"
    />
    <TemperatureSensorInstance
      x="403"
      y="621.2099609375"
      tag-id="1038-46"
      v-bind="temperatureSensors['1038-46']"
      :orientation="ComponentOrientation.Down"
    />
    <TemperatureSensorInstance
      x="197"
      y="518.2099609375"
      tag-id="1038-66"
      v-bind="temperatureSensors['1038-66']"
      :orientation="ComponentOrientation.Left"
    />
    <TemperatureSensorInstance
      x="401"
      y="461.2099609375"
      tag-id="1038-26"
      v-bind="temperatureSensors['1038-26']"
      :orientation="ComponentOrientation.Down"
    />
    <TemperatureSensorInstance
      x="562"
      y="461.2099609375"
      tag-id="1038-25"
      v-bind="temperatureSensors['1038-25']"
      :orientation="ComponentOrientation.Down"
    />
    <TemperatureSensorInstance
      x="911"
      y="462.2099609375"
      tag-id="1038-51"
      v-bind="temperatureSensors['1038-51']"
      :orientation="ComponentOrientation.Down"
    />
  </g>
</template>
