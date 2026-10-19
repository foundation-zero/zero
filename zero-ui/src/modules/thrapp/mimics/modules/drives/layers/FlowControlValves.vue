<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { ACTUATED_VALVE_WIDTH } from "../../../components/actuated-valve";
import { getTooltipContexts } from "../../../data";
import { FlowControlValveInstance } from "../../../instances";
import FlowControlLabelInstance from "../../../instances/FlowControlLabelInstance.vue";

const flowControlValves = getTooltipContexts(MimicComponentType.FlowControlValve, [
  "1065-02",
  "1065-03",
]);
</script>

<template>
  <g>
    <FlowControlValveInstance
      x="682.1582"
      y="68"
      :orientation="ComponentOrientation.Up"
      v-bind="flowControlValves['1065-02']"
    >
      <FlowControlLabelInstance
        target-x="682.1582"
        :target-width="ACTUATED_VALVE_WIDTH"
        y="102.916"
        :tag-id="flowControlValves['1065-02'].tooltip?.yardTag"
        :valve="flowControlValves['1065-02'].source"
      />
    </FlowControlValveInstance>
    <FlowControlValveInstance
      x="682.1582"
      y="502.916"
      :orientation="ComponentOrientation.Up"
      v-bind="flowControlValves['1065-03']"
    >
      <FlowControlLabelInstance
        target-x="682.1582"
        :target-width="ACTUATED_VALVE_WIDTH"
        y="538"
        :tag-id="flowControlValves['1065-03'].tooltip?.yardTag"
        :valve="flowControlValves['1065-03'].source"
      />
    </FlowControlValveInstance>
  </g>
</template>
