<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { MixValveInstance, SwitchValveInstance } from "../../../instances";
import FlowControlLabelInstance from "../../../instances/FlowControlLabelInstance.vue";
import FlowControlValveInstance from "../../../instances/FlowControlValveInstance.vue";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";
import ThreeWaySwitchValveInstance from "../../../instances/ThreeWaySwitchValveInstance.vue";
import ThreeWayValveLabelInstance from "../../../instances/ThreeWayValveLabelInstance.vue";
import { THRUSTERS_MIMIC_DATA } from "../data";

const switchValves = THRUSTERS_MIMIC_DATA[MimicComponentType.SwitchValve];
const flowControlValves = THRUSTERS_MIMIC_DATA[MimicComponentType.FlowControlValve];
const mixValves = THRUSTERS_MIMIC_DATA[MimicComponentType.MixValve];
const threeWaySwitchValves = THRUSTERS_MIMIC_DATA[MimicComponentType.ThreeWaySwitchValve];
</script>

<template>
  <g>
    <ThreeWaySwitchValveInstance
      x="414"
      y="193"
      :orientation="ComponentOrientation.Up"
      v-bind="threeWaySwitchValves['1091-01']"
    >
      <TagLabelInstance
        x="416"
        y="179"
        tag-id="1091-01"
      />
    </ThreeWaySwitchValveInstance>
    <ThreeWaySwitchValveInstance
      x="414"
      y="449.5"
      :orientation="ComponentOrientation.Down"
      v-bind="threeWaySwitchValves['1091-02']"
    >
      <TagLabelInstance
        x="416"
        y="484"
        tag-id="1091-02"
      />
    </ThreeWaySwitchValveInstance>
    <SwitchValveInstance
      x="575"
      y="346"
      :orientation="ComponentOrientation.Up"
      v-bind="switchValves['1066-03']"
    >
      <TagLabelInstance
        x="575"
        y="332"
        tag-id="1066-03"
      />
    </SwitchValveInstance>

    <FlowControlValveInstance
      x="214"
      y="193"
      :orientation="ComponentOrientation.Up"
      v-bind="flowControlValves['1215']"
    >
      <FlowControlLabelInstance
        x="218"
        y="163"
        tag-id="1215"
        :valve="flowControlValves['1215'].source"
      />
    </FlowControlValveInstance>
    <FlowControlValveInstance
      x="214"
      y="449"
      :orientation="ComponentOrientation.Up"
      v-bind="flowControlValves['1064-02']"
      ><FlowControlLabelInstance
        x="214"
        y="418"
        tag-id="1064-02"
        :valve="flowControlValves['1064-02'].source"
      />
    </FlowControlValveInstance>

    <MixValveInstance
      x="759.5"
      y="242"
      :orientation="ComponentOrientation.Down"
      v-bind="mixValves['1214-01']"
    >
      <ThreeWayValveLabelInstance
        x="755"
        y="273"
        tag-id="1214-01"
        :valve="mixValves['1214-01'].source"
      />
    </MixValveInstance>
    <MixValveInstance
      x="693.5"
      y="346"
      :orientation="ComponentOrientation.Up"
      v-bind="mixValves['1074']"
    >
      <ThreeWayValveLabelInstance
        x="689"
        y="315"
        tag-id="1074"
        :valve="mixValves['1074'].source"
      />
    </MixValveInstance>
  </g>
</template>
