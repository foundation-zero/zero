<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { LevelLabelInstance, LevelSensorInstance } from "../../../instances";
import { DHW_MIMIC_DATA } from "../data";

const levelSensors = DHW_MIMIC_DATA[MimicComponentType.LevelSensor];
</script>

<template>
  <g>
    <LevelSensorInstance
      x="559"
      y="109.2099609375"
      v-bind="levelSensors['1056-01']"
      :orientation="ComponentOrientation.Left"
    >
      <LevelLabelInstance
        x="565"
        y="71"
        :tag-id="levelSensors['1056-01'].tooltip?.yardTag"
        :level="levelSensors['1056-01'].source"
      />
    </LevelSensorInstance>
    <LevelSensorInstance
      x="921"
      y="109.2099609375"
      v-bind="levelSensors['1056-02']"
      :orientation="ComponentOrientation.Left"
    >
      <LevelLabelInstance
        x="926"
        y="71"
        :tag-id="levelSensors['1056-02'].tooltip?.yardTag"
        :level="levelSensors['1056-02'].source"
      />
    </LevelSensorInstance>
    <LevelSensorInstance
      x="1260"
      y="109.2099609375"
      v-bind="levelSensors['1056-03']"
      :orientation="ComponentOrientation.Left"
    >
      <LevelLabelInstance
        x="1266"
        y="71"
        :tag-id="levelSensors['1056-03'].tooltip?.yardTag"
        :level="levelSensors['1056-03'].source"
      />
    </LevelSensorInstance>
  </g>
</template>
