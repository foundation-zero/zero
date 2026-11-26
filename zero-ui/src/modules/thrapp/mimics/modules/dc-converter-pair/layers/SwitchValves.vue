<script setup lang="ts">
import { computed } from "vue";
import { BranchFields } from "../dc-converter-pair.types";
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { ACTUATED_VALVE_WIDTH } from "../../../components/actuated-valve";
import { getTooltipContext } from "../../../data";
import { SwitchValveInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";

const props = defineProps<{ fields: BranchFields<MimicComponentType.SwitchValve> }>();

const getContext = getTooltipContext(MimicComponentType.SwitchValve);
// Not `map(getContext)`: map passes the index, which getContext takes as `arrayIndexIfMultiple`.
const switchValves = computed(() => props.fields.map((field) => getContext(field)));
</script>

<template>
  <g>
    <SwitchValveInstance
      x="300"
      y="142"
      :orientation="ComponentOrientation.Up"
      v-bind="switchValves[0]"
    >
      <TagLabelInstance
        target-x="300"
        :target-width="ACTUATED_VALVE_WIDTH"
        y="123"
        :tag-id="switchValves[0].tooltip?.yardTag"
      />
    </SwitchValveInstance>
    <SwitchValveInstance
      x="300"
      y="355"
      :orientation="ComponentOrientation.Up"
      v-bind="switchValves[1]"
    >
      <TagLabelInstance
        target-x="300"
        :target-width="ACTUATED_VALVE_WIDTH"
        y="333"
        :tag-id="switchValves[1].tooltip?.yardTag"
      />
    </SwitchValveInstance>
  </g>
</template>
