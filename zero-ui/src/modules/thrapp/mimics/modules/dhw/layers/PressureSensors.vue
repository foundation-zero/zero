<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PressureSensorInstance } from "../../../instances";
import PressureLabelInstance from "../../../instances/PressureLabelInstance.vue";
import { DHW_MIMIC_DATA } from "../data";

const pressureSensors = DHW_MIMIC_DATA[MimicComponentType.PressureSensor];
</script>

<template>
  <g>
    <PressureSensorInstance
      x="559"
      y="109.2099609375"
      tag-id="1056-01"
      v-bind="pressureSensors['1056-01']"
      :orientation="ComponentOrientation.Left"
    >
      <PressureLabelInstance
        x="565"
        y="71"
        tag-id="1056-01"
        :pressure="pressureSensors['1056-01'].source"
      />
    </PressureSensorInstance>
    <PressureSensorInstance
      x="921"
      y="109.2099609375"
      tag-id="1056-02"
      v-bind="pressureSensors['1056-02']"
      :orientation="ComponentOrientation.Left"
    >
      <PressureLabelInstance
        x="926"
        y="71"
        tag-id="1056-02"
        :pressure="pressureSensors['1056-02'].source"
      />
    </PressureSensorInstance>
    <PressureSensorInstance
      x="1260"
      y="109.2099609375"
      tag-id="1056-03"
      v-bind="pressureSensors['1056-03']"
      :orientation="ComponentOrientation.Left"
    >
      <PressureLabelInstance
        x="1266"
        y="71"
        tag-id="1056-03"
        :pressure="pressureSensors['1056-03'].source"
      />
    </PressureSensorInstance>
    <PressureSensorInstance
      x="289"
      y="221.2099609375"
      tag-id="1097-11"
      v-bind="pressureSensors['1097-11']"
      :orientation="ComponentOrientation.Down"
    >
      <PressureLabelInstance
        x="277"
        y="186"
        tag-id="1097-11"
        :pressure="pressureSensors['1097-11'].source"
      />
    </PressureSensorInstance>
  </g>
</template>
