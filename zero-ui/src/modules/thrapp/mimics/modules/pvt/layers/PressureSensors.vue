<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PRESSURE_SENSOR_WIDTH } from "../../../components/pressure-sensor";
import { getTooltipContexts } from "../../../data";
import { PressureSensorInstance } from "../../../instances";
import PressureLabelInstance from "../../../instances/PressureLabelInstance.vue";

const pressureSensors = getTooltipContexts(MimicComponentType.PressureSensor, [
  "1097-03",
  "1097-04",
  "1097-05",
]);
</script>

<template>
  <g>
    <PressureSensorInstance
      x="617"
      y="191"
      :orientation="ComponentOrientation.Down"
      v-bind="pressureSensors['1097-03']"
    >
      <PressureLabelInstance
        :target-x="614"
        :target-width="PRESSURE_SENSOR_WIDTH"
        y="154.5"
        :tag-id="pressureSensors['1097-03'].tooltip?.yardTag"
        :pressure="pressureSensors['1097-03'].source"
      />
    </PressureSensorInstance>
    <PressureSensorInstance
      x="612"
      y="386"
      :orientation="ComponentOrientation.Down"
      v-bind="pressureSensors['1097-04']"
    >
      <PressureLabelInstance
        :target-x="614"
        :target-width="PRESSURE_SENSOR_WIDTH"
        y="350.5"
        :tag-id="pressureSensors['1097-04'].tooltip?.yardTag"
        :pressure="pressureSensors['1097-04'].source"
      />
    </PressureSensorInstance>
    <PressureSensorInstance
      x="615"
      y="610"
      :orientation="ComponentOrientation.Down"
      v-bind="pressureSensors['1097-05']"
    >
      <PressureLabelInstance
        :target-x="614"
        :target-width="PRESSURE_SENSOR_WIDTH"
        y="573.5"
        :tag-id="pressureSensors['1097-05'].tooltip?.yardTag"
        :pressure="pressureSensors['1097-05'].source"
      />
    </PressureSensorInstance>
  </g>
</template>
