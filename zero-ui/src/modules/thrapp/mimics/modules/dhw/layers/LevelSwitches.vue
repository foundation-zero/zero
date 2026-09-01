<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { LevelSwitchInstance, TagLabelInstance } from "../../../instances";
import { DHW_MIMIC_DATA } from "../data";

const levelSensors = DHW_MIMIC_DATA[MimicComponentType.LevelSwitch];
</script>

<template>
  <g>
    <LevelSwitchInstance
      x="560.0000076293945"
      y="10.2178955078125"
      :orientation="ComponentOrientation.Left"
      v-bind="levelSensors['1098-01']"
    >
      <TagLabelInstance
        x="598"
        y="12"
        :tag-id="levelSensors['1098-01'].tooltip?.yardTag"
      />
    </LevelSwitchInstance>
    <LevelSwitchInstance
      x="920.0806884765625"
      y="10.2178955078125"
      :orientation="ComponentOrientation.Left"
      v-bind="levelSensors['1098-02']"
    >
      <TagLabelInstance
        x="956"
        y="12"
        :tag-id="levelSensors['1098-02'].tooltip?.yardTag"
      />
    </LevelSwitchInstance>
    <LevelSwitchInstance
      x="1260.0806884765625"
      y="10.2178955078125"
      :orientation="ComponentOrientation.Left"
      v-bind="levelSensors['1098-03']"
    >
      <TagLabelInstance
        x="1295"
        y="12"
        :tag-id="levelSensors['1098-03'].tooltip?.yardTag"
      />
    </LevelSwitchInstance>
  </g>
</template>
