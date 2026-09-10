<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { TEMPERATURE_SENSOR_WIDTH } from "../../../components/temperature-sensor";
import { TemperatureSensorInstance } from "../../../instances";
import TemperatureLabelInstance from "../../../instances/TemperatureLabelInstance.vue";
import { THRUSTERS_MIMIC_DATA } from "../data";

const temperatureSensors = THRUSTERS_MIMIC_DATA[MimicComponentType.TemperatureSensor];
</script>

<template>
  <g>
    <TemperatureSensorInstance
      x="280"
      y="181"
      :orientation="ComponentOrientation.Down"
      v-bind="temperatureSensors['1038-01']"
    >
      <TemperatureLabelInstance
        x="320"
        y="165"
        :tag-id="temperatureSensors['1038-01'].tooltip?.yardTag"
        :temperature="temperatureSensors['1038-01'].source"
      />
    </TemperatureSensorInstance>
    <TemperatureSensorInstance
      x="280"
      y="438"
      :orientation="ComponentOrientation.Down"
      v-bind="temperatureSensors['1038-02']"
    >
      <TemperatureLabelInstance
        x="320"
        y="420"
        :tag-id="temperatureSensors['1038-02'].tooltip?.yardTag"
        :temperature="temperatureSensors['1038-02'].source"
      />
    </TemperatureSensorInstance>
    <TemperatureSensorInstance
      x="837.963"
      y="555"
      :orientation="ComponentOrientation.Down"
      v-bind="temperatureSensors['1038-28']"
    >
      <TemperatureLabelInstance
        :target-x="837.963"
        :target-width="TEMPERATURE_SENSOR_WIDTH"
        y="515"
        :tag-id="temperatureSensors['1038-28'].tooltip?.yardTag"
        :temperature="temperatureSensors['1038-28'].source"
      />
    </TemperatureSensorInstance>
    <TemperatureSensorInstance
      x="635"
      y="333"
      :orientation="ComponentOrientation.Down"
      v-bind="temperatureSensors['1038-30']"
    >
      <TemperatureLabelInstance
        :target-x="635"
        :target-width="TEMPERATURE_SENSOR_WIDTH"
        y="293"
        :tag-id="temperatureSensors['1038-30'].tooltip?.yardTag"
        :temperature="temperatureSensors['1038-30'].source"
      />
    </TemperatureSensorInstance>
  </g>
</template>
