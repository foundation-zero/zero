<script setup lang="ts">
import { ComponentOrientation } from "../../../components";
import { PRESSURE_SENSOR_WIDTH } from "../../../components/pressure-sensor";
import { PressureLabelInstance, PressureSensorInstance } from "../../../instances";
import { DRIVES_PRESSURE_SENSOR_DATA } from "../data";

const pressureSensors = DRIVES_PRESSURE_SENSOR_DATA.PressureSensor;
</script>

<template>
  <g>
    <PressureSensorInstance
      x="1554.6582"
      y="645.416"
      :orientation="ComponentOrientation.Down"
      v-bind="pressureSensors['1097-10']"
    >
      <PressureLabelInstance
        target-x="1550.6582"
        :target-width="PRESSURE_SENSOR_WIDTH"
        y="598.916"
        :tag-id="pressureSensors['1097-10'].tooltip?.yardTag"
        :pressure="pressureSensors['1097-10'].source"
      />
    </PressureSensorInstance>
  </g>
</template>
