<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { ACTUATED_VALVE_WIDTH } from "../../../components/actuated-valve";
import { getTooltipContexts } from "../../../data";
import { SwitchValveInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";

const switchValves = getTooltipContexts(MimicComponentType.SwitchValve, [
  "1068-01",
  "1068-02",
  "1068-03",
  "1068-04",
]);
</script>

<template>
  <g>
    <SwitchValveInstance
      x="299"
      y="142"
      :orientation="ComponentOrientation.Up"
      v-bind="switchValves['1068-01']"
    >
      <TagLabelInstance
        target-x="299"
        :target-width="ACTUATED_VALVE_WIDTH"
        y="119"
        :tag-id="switchValves['1068-01'].tooltip?.yardTag"
      />
    </SwitchValveInstance>
    <SwitchValveInstance
      x="299"
      y="355"
      :orientation="ComponentOrientation.Up"
      v-bind="switchValves['1068-02']"
    >
      <TagLabelInstance
        target-x="299"
        :target-width="ACTUATED_VALVE_WIDTH"
        y="329"
        :tag-id="switchValves['1068-02'].tooltip?.yardTag"
      />
    </SwitchValveInstance>
    <SwitchValveInstance
      x="299"
      y="566"
      :orientation="ComponentOrientation.Up"
      v-bind="switchValves['1068-03']"
    >
      <TagLabelInstance
        target-x="299"
        :target-width="ACTUATED_VALVE_WIDTH"
        y="540"
        :tag-id="switchValves['1068-03'].tooltip?.yardTag"
      />
    </SwitchValveInstance>
    <SwitchValveInstance
      x="299"
      y="761"
      :orientation="ComponentOrientation.Up"
      v-bind="switchValves['1068-04']"
    >
      <TagLabelInstance
        target-x="299"
        :target-width="ACTUATED_VALVE_WIDTH"
        y="733"
        :tag-id="switchValves['1068-04'].tooltip?.yardTag"
      />
    </SwitchValveInstance>
  </g>
</template>
