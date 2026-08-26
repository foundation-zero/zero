<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PRESSURE_SENSOR_WIDTH } from "../../../components/pressure-sensor";
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
        :target-x="559 + 10"
        :target-width="PRESSURE_SENSOR_WIDTH"
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
        :target-x="921 + 10"
        :target-width="PRESSURE_SENSOR_WIDTH"
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
        :target-x="1260 + 10"
        :target-width="PRESSURE_SENSOR_WIDTH"
        y="71"
        :tag-id="levelSensors['1056-03'].tooltip?.yardTag"
        :level="levelSensors['1056-03'].source"
      />
    </LevelSensorInstance>
  </g>
</template>
