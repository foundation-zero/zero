<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { TemperatureSensorInstance } from "../../../instances";
import TemperatureLabelInstance from "../../../instances/TemperatureLabelInstance.vue";
import { THRUSTERS_MIMIC_DATA } from "../data";

const temperatureSensors = THRUSTERS_MIMIC_DATA[MimicComponentType.TemperatureSensor];
</script>

<template>
  <g>
    <TemperatureSensorInstance
      x="286.512"
      y="181"
      tag-id="1038-01"
      :orientation="ComponentOrientation.Down"
      v-bind="temperatureSensors['1038-01']"
    >
      <TemperatureLabelInstance
        x="280"
        y="138"
        tag-id="1038-01"
        :temperature="temperatureSensors['1038-01'].source"
      />
    </TemperatureSensorInstance>
    <TemperatureSensorInstance
      x="286.512"
      y="438"
      tag-id="1038-02"
      :orientation="ComponentOrientation.Down"
      v-bind="temperatureSensors['1038-02']"
    >
      <TemperatureLabelInstance
        x="280"
        y="398"
        tag-id="1038-02"
        :temperature="temperatureSensors['1038-02'].source"
      />
    </TemperatureSensorInstance>
    <TemperatureSensorInstance
      x="837.963"
      y="555"
      tag-id="1038-28"
      :orientation="ComponentOrientation.Down"
      v-bind="temperatureSensors['1038-28']"
    >
      <TemperatureLabelInstance
        x="827"
        y="515"
        tag-id="1038-28"
        :temperature="temperatureSensors['1038-28'].source"
      />
    </TemperatureSensorInstance>
    <TemperatureSensorInstance
      x="635"
      y="333"
      tag-id="1038-30"
      :orientation="ComponentOrientation.Down"
      v-bind="temperatureSensors['1038-30']"
    >
      <TemperatureLabelInstance
        x="631"
        y="293"
        tag-id="1038-30"
        :temperature="temperatureSensors['1038-30'].source"
      />
    </TemperatureSensorInstance>
  </g>
</template>
