<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { getTooltipContexts } from "../../../data";
import { LevelSwitchInstance, TagLabelInstance } from "../../../instances";

const levelSwitches = getTooltipContexts(MimicComponentType.LevelSwitch, [
  "1098-01",
  "1098-02",
  "1098-03",
]);
</script>

<template>
  <g>
    <LevelSwitchInstance
      x="560.0000076293945"
      y="10.2178955078125"
      :orientation="ComponentOrientation.Left"
      v-bind="levelSwitches['1098-01']"
    >
      <TagLabelInstance
        x="598"
        y="12"
        :tag-id="levelSwitches['1098-01'].tooltip?.yardTag"
      />
    </LevelSwitchInstance>
    <LevelSwitchInstance
      x="920.0806884765625"
      y="10.2178955078125"
      :orientation="ComponentOrientation.Left"
      v-bind="levelSwitches['1098-02']"
    >
      <TagLabelInstance
        x="956"
        y="12"
        :tag-id="levelSwitches['1098-02'].tooltip?.yardTag"
      />
    </LevelSwitchInstance>
    <LevelSwitchInstance
      x="1260.0806884765625"
      y="10.2178955078125"
      :orientation="ComponentOrientation.Left"
      v-bind="levelSwitches['1098-03']"
    >
      <TagLabelInstance
        x="1295"
        y="12"
        :tag-id="levelSwitches['1098-03'].tooltip?.yardTag"
      />
    </LevelSwitchInstance>
  </g>
</template>
