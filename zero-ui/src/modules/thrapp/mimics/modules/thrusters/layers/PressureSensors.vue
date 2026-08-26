<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PressureSensorInstance } from "../../../instances";
import PressureLabelInstance from "../../../instances/PressureLabelInstance.vue";
import { THRUSTERS_MIMIC_DATA } from "../data";

const pressureSensors = THRUSTERS_MIMIC_DATA[MimicComponentType.PressureSensor];
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
        x="453"
        y="515"
        :tag-id="pressureSensors['1097-01'].tooltip?.yardTag"
        :pressure="pressureSensors['1097-01'].source"
      />
    </PressureSensorInstance>
    <PressureSensorInstance
      x="938.637"
      y="229"
      :orientation="ComponentOrientation.Down"
      v-bind="pressureSensors['1097-02']"
      ><PressureLabelInstance
        x="934"
        y="193"
        :tag-id="pressureSensors['1097-02'].tooltip?.yardTag"
        :pressure="pressureSensors['1097-02'].source"
      />
    </PressureSensorInstance>
  </g>
</template>
