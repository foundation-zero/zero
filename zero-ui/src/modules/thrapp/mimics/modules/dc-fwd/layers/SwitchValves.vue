<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { ACTUATED_VALVE_WIDTH } from "../../../components/actuated-valve";
import { getTooltipContexts } from "../../../data";
import { SwitchValveInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";

const switchValves = getTooltipContexts(MimicComponentType.SwitchValve, ["1068-05", "1068-06"]);
</script>

<template>
  <g>
    <SwitchValveInstance
      x="300"
      y="142"
      :orientation="ComponentOrientation.Up"
      v-bind="switchValves['1068-05']"
    >
      <TagLabelInstance
        target-x="300"
        :target-width="ACTUATED_VALVE_WIDTH"
        y="119"
        :tag-id="switchValves['1068-05'].tooltip?.yardTag"
      />
    </SwitchValveInstance>
    <SwitchValveInstance
      x="300"
      y="355"
      :orientation="ComponentOrientation.Up"
      v-bind="switchValves['1068-06']"
    >
      <TagLabelInstance
        target-x="300"
        :target-width="ACTUATED_VALVE_WIDTH"
        y="329"
        :tag-id="switchValves['1068-06'].tooltip?.yardTag"
      />
    </SwitchValveInstance>
  </g>
</template>
