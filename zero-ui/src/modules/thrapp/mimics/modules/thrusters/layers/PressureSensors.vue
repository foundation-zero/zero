<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PRESSURE_SENSOR_WIDTH } from "../../../components/pressure-sensor";
import { getTooltipContexts } from "../../../data";
import { PressureSensorInstance } from "../../../instances";
import PressureLabelInstance from "../../../instances/PressureLabelInstance.vue";

const pressureSensors = getTooltipContexts(MimicComponentType.PressureSensor, [
  "1097-01",
  "1097-02",
  "1097-06",
]);
</script>

<template>
  <g>
    <PressureSensorInstance
      x="465.441"
      y="555"
      :orientation="ComponentOrientation.Down"
      v-bind="pressureSensors['1097-01']"
    >
      <PressureLabelInstance
        :target-x="465.441"
        :target-width="PRESSURE_SENSOR_WIDTH"
        y="515"
        :tag-id="pressureSensors['1097-01'].tooltip?.yardTag"
        :pressure="pressureSensors['1097-01'].source"
      />
    </PressureSensorInstance>
    <PressureSensorInstance
      x="201"
      y="118"
      :orientation="ComponentOrientation.Left"
      v-bind="pressureSensors['1097-02']"
    >
      <PressureLabelInstance
        x="236"
        y="114"
        :tag-id="pressureSensors['1097-02'].tooltip?.yardTag"
        :pressure="pressureSensors['1097-02'].source"
      />
    </PressureSensorInstance>
    <PressureSensorInstance
      x="853"
      y="312"
      :orientation="ComponentOrientation.Down"
      v-bind="pressureSensors['1097-06']"
    >
      <PressureLabelInstance
        x="843"
        y="276"
        :tag-id="pressureSensors['1097-06'].tooltip?.yardTag"
        :pressure="pressureSensors['1097-06'].source"
      />
    </PressureSensorInstance>
  </g>
</template>
