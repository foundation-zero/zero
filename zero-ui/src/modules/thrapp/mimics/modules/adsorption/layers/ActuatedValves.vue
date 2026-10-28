<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { getTooltipContexts } from "../../../data";
import {
  FlowControlValveInstance,
  MixValveInstance,
  SwitchValveInstance,
  TagLabelInstance,
  ThreeWayValveLabelInstance,
} from "../../../instances";
import FlowControlLabelInstance from "../../../instances/FlowControlLabelInstance.vue";

const mixValves = getTooltipContexts(MimicComponentType.MixValve, ["1046-02", "1047-01"]);
const switchValves = getTooltipContexts(MimicComponentType.SwitchValve, ["1187-01"]);
const flowControlValves = getTooltipContexts(MimicComponentType.FlowControlValve, ["1062-03"]);
</script>

<template>
  <g>
    <MixValveInstance
      x="1359.35"
      y="226.87"
      :orientation="ComponentOrientation.Down"
      v-bind="mixValves['1046-02']"
    >
      <ThreeWayValveLabelInstance
        x="1346.35"
        y="262.18"
        :tag-id="mixValves['1046-02'].tooltip?.yardTag"
        :valve="mixValves['1046-02'].source"
      />
    </MixValveInstance>
    <MixValveInstance
      x="549"
      y="380"
      :orientation="ComponentOrientation.Up"
      v-bind="mixValves['1047-01']"
    >
      <ThreeWayValveLabelInstance
        x="540"
        y="337.5"
        :tag-id="mixValves['1047-01'].tooltip?.yardTag"
        :valve="mixValves['1047-01'].source"
      />
    </MixValveInstance>
    <SwitchValveInstance
      x="97"
      y="269"
      :orientation="ComponentOrientation.Up"
      v-bind="switchValves['1187-01']"
    >
      <TagLabelInstance
        x="98.5"
        y="240"
        :tag-id="switchValves['1187-01'].tooltip?.yardTag"
      />
    </SwitchValveInstance>
    <FlowControlValveInstance
      x="230"
      y="323"
      :orientation="ComponentOrientation.Right"
      v-bind="flowControlValves['1062-03']"
    >
      <FlowControlLabelInstance
        x="271"
        y="294.5"
        :tag-id="flowControlValves['1062-03'].tooltip?.yardTag"
        :valve="flowControlValves['1062-03'].source"
      />
    </FlowControlValveInstance>
  </g>
</template>
