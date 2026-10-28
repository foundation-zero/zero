<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PRESSURE_SENSOR_WIDTH } from "../../../components/pressure-sensor";
import { getTooltipContexts } from "../../../data";
import { PressureLabelInstance, PressureSensorInstance } from "../../../instances";

const pressureSensors = getTooltipContexts(MimicComponentType.PressureSensor, [
  "1097-07",
  "1097-08",
  "1097-09",
]);
</script>

<template>
  <PressureSensorInstance
    x="564"
    y="167"
    :orientation="ComponentOrientation.Down"
    v-bind="pressureSensors['1097-07']"
  >
    <PressureLabelInstance
      target-x="567"
      :target-width="PRESSURE_SENSOR_WIDTH"
      y="131.646"
      :tag-id="pressureSensors['1097-07'].tooltip?.yardTag"
      :pressure="pressureSensors['1097-07'].source"
    />
  </PressureSensorInstance>
  <PressureSensorInstance
    x="564"
    y="381"
    :orientation="ComponentOrientation.Down"
    v-bind="pressureSensors['1097-08']"
  >
    <PressureLabelInstance
      target-x="567"
      :target-width="PRESSURE_SENSOR_WIDTH"
      y="346.646"
      :tag-id="pressureSensors['1097-08'].tooltip?.yardTag"
      :pressure="pressureSensors['1097-08'].source"
    />
  </PressureSensorInstance>
  <PressureSensorInstance
    x="564"
    y="610"
    :orientation="ComponentOrientation.Down"
    v-bind="pressureSensors['1097-09']"
  >
    <PressureLabelInstance
      target-x="567"
      :target-width="PRESSURE_SENSOR_WIDTH"
      y="571.646"
      :tag-id="pressureSensors['1097-09'].tooltip?.yardTag"
      :pressure="pressureSensors['1097-09'].source"
    />
  </PressureSensorInstance>
</template>
