<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { ACTUATED_VALVE_WIDTH, ValveLeg, ValvePortName } from "../../../components/actuated-valve";
import { getTooltipContexts } from "../../../data";
import {
  MixValveInstance,
  SwitchValveInstance,
  ThreeWayValveLabelInstance,
} from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";

const switchValves = getTooltipContexts(MimicComponentType.SwitchValve, [
  "1067-01",
  "1067-02",
  "1069-01",
]);
const mixValves = getTooltipContexts(MimicComponentType.MixValve, [
  "1044-01",
  "1044-02",
  "1043-01",
  "1047-02",
]);
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
        :target-x="252"
        :target-width="ACTUATED_VALVE_WIDTH"
        y="232"
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
        :target-x="252"
        :target-width="ACTUATED_VALVE_WIDTH"
        y="430"
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
        :target-x="252"
        :target-width="ACTUATED_VALVE_WIDTH"
        y="652"
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
        x="688.5"
        y="165.5"
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
        x="688.5"
        y="360.5"
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
        x="688.5"
        y="587.5"
        :tag-id="mixValves['1043-01'].tooltip?.yardTag"
        :valve="mixValves['1043-01'].source"
      />
    </MixValveInstance>
    <MixValveInstance
      x="966"
      y="515"
      :orientation="ComponentOrientation.Left"
      v-bind="mixValves['1047-02']"
      :legs="{
        [ValveLeg.Left]: ValvePortName.AB,
        [ValveLeg.Right]: ValvePortName.A,
        [ValveLeg.Bottom]: ValvePortName.B,
      }"
    >
      <ThreeWayValveLabelInstance
        x="997"
        y="477.5"
        :tag-id="mixValves['1047-02'].tooltip?.yardTag"
        :valve="mixValves['1047-02'].source"
      />
    </MixValveInstance>
  </g>
</template>
