<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PressureSensorInstance } from "../../../instances";
import PressureLabelInstance from "../../../instances/PressureLabelInstance.vue";
import { PVT_MIMIC_DATA } from "../data";

const pressureSensors = PVT_MIMIC_DATA[MimicComponentType.PressureSensor];
</script>

<template>
  <g>
    <PressureSensorInstance
      x="610"
      y="191"
      :orientation="ComponentOrientation.Down"
      v-bind="pressureSensors['1097-03']"
    >
      <PressureLabelInstance
        x="605"
        y="151"
        :tag-id="pressureSensors['1097-03'].tooltip?.yardTag"
        :pressure="pressureSensors['1097-03'].source"
      />
    </PressureSensorInstance>
    <PressureSensorInstance
      x="610"
      y="386"
      :orientation="ComponentOrientation.Down"
      v-bind="pressureSensors['1097-04']"
    >
      <PressureLabelInstance
        x="605"
        y="348"
        :tag-id="pressureSensors['1097-04'].tooltip?.yardTag"
        :pressure="pressureSensors['1097-04'].source"
      />
    </PressureSensorInstance>
    <PressureSensorInstance
      x="610"
      y="610"
      :orientation="ComponentOrientation.Down"
      v-bind="pressureSensors['1097-05']"
    >
      <PressureLabelInstance
        x="605"
        y="570"
        :tag-id="pressureSensors['1097-05'].tooltip?.yardTag"
        :pressure="pressureSensors['1097-05'].source"
      />
    </PressureSensorInstance>
    <PressureSensorInstance
      x="1044"
      y="279"
      :orientation="ComponentOrientation.Down"
      v-bind="pressureSensors['1097-06']"
    >
      <PressureLabelInstance
        x="1044"
        y="239"
        :tag-id="pressureSensors['1097-06'].tooltip?.yardTag"
        :pressure="pressureSensors['1097-06'].source"
      />
    </PressureSensorInstance>
  </g>
</template>
