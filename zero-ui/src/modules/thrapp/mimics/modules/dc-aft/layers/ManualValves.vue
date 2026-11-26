<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import LayerFilter from "../../../components/layer-filter/LayerFilter.vue";
import { LayerFilterOption } from "../../../components/layer-filter/layer-filter.provider";
import { MANUAL_VALVE_WIDTH, ManualValveType } from "../../../components/manual-valve";
import { getTooltipContexts } from "../../../data";
import { ManualValveInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";

const manualValves = getTooltipContexts(MimicComponentType.ManualValve, ["1167-02", "1167-01"]);
</script>

<template>
  <LayerFilter :filter="LayerFilterOption.ManualComponents">
    <ManualValveInstance
      x="299"
      y="443"
      :valve-type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves['1167-02']"
    >
      <TagLabelInstance
        target-x="299"
        :target-width="MANUAL_VALVE_WIDTH"
        y="434"
        :tag-id="manualValves['1167-02'].tooltip?.yardTag"
      />
    </ManualValveInstance>
    <ManualValveInstance
      x="299"
      y="637"
      :valve-type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves['1167-01']"
    >
      <TagLabelInstance
        target-x="299"
        :target-width="MANUAL_VALVE_WIDTH"
        y="629"
        :tag-id="manualValves['1167-01'].tooltip?.yardTag"
      />
    </ManualValveInstance>
  </LayerFilter>
</template>
