<script setup lang="ts">
import { computed } from "vue";
import { BranchFields } from "../dc-converter-pair.types";
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import LayerFilter from "../../../components/layer-filter/LayerFilter.vue";
import { LayerFilterOption } from "../../../components/layer-filter/layer-filter.provider";
import { MANUAL_VALVE_WIDTH, ManualValveType } from "../../../components/manual-valve";
import { getTooltipContext } from "../../../data";
import { ManualValveInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";

const props = defineProps<{ fields: BranchFields<MimicComponentType.ManualValve> }>();

const getContext = getTooltipContext(MimicComponentType.ManualValve);
// Not `map(getContext)`: map passes the index, which getContext takes as `arrayIndexIfMultiple`.
const manualValves = computed(() => props.fields.map((field) => getContext(field)));
</script>

<template>
  <LayerFilter :filter="LayerFilterOption.ManualComponents">
    <ManualValveInstance
      x="296"
      y="21"
      :valve-type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves[0]"
    >
      <TagLabelInstance
        target-x="296"
        :target-width="MANUAL_VALVE_WIDTH"
        y="7"
        :tag-id="manualValves[0].tooltip?.yardTag"
      />
    </ManualValveInstance>
    <ManualValveInstance
      x="297"
      y="235"
      :valve-type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves[1]"
    >
      <TagLabelInstance
        target-x="297"
        :target-width="MANUAL_VALVE_WIDTH"
        y="223"
        :tag-id="manualValves[1].tooltip?.yardTag"
      />
    </ManualValveInstance>
  </LayerFilter>
</template>
