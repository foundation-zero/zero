<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PressureLabelInstance, PressureSensorInstance } from "../../../instances";
import { DHW_MIMIC_DATA } from "../data";

const pressureSensors = DHW_MIMIC_DATA[MimicComponentType.PressureSensor];
</script>

<template>
  <g>
    <PressureSensorInstance
      x="289"
      y="221.2099609375"
      v-bind="pressureSensors['1097-11']"
      :orientation="ComponentOrientation.Down"
    >
      <PressureLabelInstance
        x="277"
        y="186"
        :tag-id="pressureSensors['1097-11'].tooltip?.yardTag"
        :pressure="pressureSensors['1097-11'].source"
      />
    </PressureSensorInstance>
  </g>
</template>
