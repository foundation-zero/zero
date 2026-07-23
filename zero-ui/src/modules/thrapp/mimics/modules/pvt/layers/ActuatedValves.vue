<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import {
  MixValveInstance,
  SwitchValveInstance,
  ThreeWayValveLabelInstance,
} from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";
import { PVT_MIMIC_DATA } from "../data";

const switchValves = PVT_MIMIC_DATA[MimicComponentType.SwitchValve];
const mixValves = PVT_MIMIC_DATA[MimicComponentType.MixValve];
</script>

<template>
  <g>
    <SwitchValveInstance
      x="249"
      y="202"
      :orientation="ComponentOrientation.Up"
      v-bind="switchValves['1067-01']"
    >
      <TagLabelInstance
        x="249"
        y="190"
        :tag-id="switchValves['1067-01'].tooltip?.yardTag"
      />
    </SwitchValveInstance>
    <SwitchValveInstance
      x="249"
      y="399"
      :orientation="ComponentOrientation.Up"
      v-bind="switchValves['1067-02']"
    >
      <TagLabelInstance
        x="249"
        y="388"
        :tag-id="switchValves['1067-02'].tooltip?.yardTag"
      />
    </SwitchValveInstance>
    <SwitchValveInstance
      x="249"
      y="622"
      :orientation="ComponentOrientation.Up"
      v-bind="switchValves['1069-01']"
    >
      <TagLabelInstance
        x="249"
        y="613"
        :tag-id="switchValves['1069-01'].tooltip?.yardTag"
      />
    </SwitchValveInstance>

    <MixValveInstance
      x="657"
      y="202"
      :orientation="ComponentOrientation.Down"
      v-bind="mixValves['1044-01']"
    >
      <ThreeWayValveLabelInstance
        x="686"
        y="176"
        :tag-id="mixValves['1044-01'].tooltip?.yardTag"
        :valve="mixValves['1044-01'].source"
      />
    </MixValveInstance>
    <MixValveInstance
      x="657"
      y="399"
      :orientation="ComponentOrientation.Down"
      v-bind="mixValves['1044-02']"
    >
      <ThreeWayValveLabelInstance
        x="686"
        y="375"
        :tag-id="mixValves['1044-02'].tooltip?.yardTag"
        :valve="mixValves['1044-02'].source"
      />
    </MixValveInstance>
    <MixValveInstance
      x="657"
      y="622"
      :orientation="ComponentOrientation.Down"
      v-bind="mixValves['1043-01']"
    >
      <ThreeWayValveLabelInstance
        x="686"
        y="598"
        :tag-id="mixValves['1043-01'].tooltip?.yardTag"
        :valve="mixValves['1043-01'].source"
      />
    </MixValveInstance>
    <MixValveInstance
      x="966"
      y="515"
      :orientation="ComponentOrientation.Left"
      v-bind="mixValves['1047-02']"
    >
      <ThreeWayValveLabelInstance
        x="994"
        y="485"
        :tag-id="mixValves['1047-02'].tooltip?.yardTag"
        :valve="mixValves['1047-02'].source"
      />
    </MixValveInstance>
  </g>
</template>
