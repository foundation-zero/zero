<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { LevelSensorInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";
import { DHW_MIMIC_DATA } from "../data";

const levelSensors = DHW_MIMIC_DATA[MimicComponentType.LevelSensor];
</script>

<template>
  <g>
    <LevelSensorInstance
      x="560.0000076293945"
      y="10.2178955078125"
      tag-id="1098-01"
      :orientation="ComponentOrientation.Left"
      v-bind="levelSensors['1098-01']"
    >
      <TagLabelInstance
        x="598"
        y="19"
        tag-id="1098-01"
      />
    </LevelSensorInstance>
    <LevelSensorInstance
      x="920.0806884765625"
      y="10.2178955078125"
      tag-id="1098-02"
      :orientation="ComponentOrientation.Left"
      v-bind="levelSensors['1098-02']"
    >
      <TagLabelInstance
        x="956"
        y="19"
        tag-id="1098-02"
      />
    </LevelSensorInstance>
    <LevelSensorInstance
      x="1260.0806884765625"
      y="10.2178955078125"
      tag-id="1098-03"
      :orientation="ComponentOrientation.Left"
      v-bind="levelSensors['1098-03']"
    >
      <TagLabelInstance
        x="1295"
        y="19"
        tag-id="1098-03"
      />
    </LevelSensorInstance>
  </g>
</template>
