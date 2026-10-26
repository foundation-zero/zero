<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PRESSURE_SENSOR_WIDTH } from "../../../components/pressure-sensor";
import { getTooltipContexts } from "../../../data";
import { PressureLabelInstance, PressureSensorInstance } from "../../../instances";

const pressureSensors = getTooltipContexts(MimicComponentType.PressureSensor, ["1097-10"]);
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
