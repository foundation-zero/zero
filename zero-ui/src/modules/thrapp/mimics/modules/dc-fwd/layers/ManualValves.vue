<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import LayerFilter from "../../../components/layer-filter/LayerFilter.vue";
import { LayerFilterOption } from "../../../components/layer-filter/layer-filter.provider";
import { MANUAL_VALVE_WIDTH, ManualValveType } from "../../../components/manual-valve";
import { getTooltipContexts } from "../../../data";
import { ManualValveInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";

const manualValves = getTooltipContexts(MimicComponentType.ManualValve, ["1067-05", "1067-06"]);
</script>

<template>
  <LayerFilter :filter="LayerFilterOption.ManualComponents">
    <ManualValveInstance
      x="296"
      y="21"
      :valve-type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves['1067-05']"
    >
      <TagLabelInstance
        target-x="296"
        :target-width="MANUAL_VALVE_WIDTH"
        y="3"
        :tag-id="manualValves['1067-05'].tooltip?.yardTag"
      />
    </ManualValveInstance>
    <ManualValveInstance
      x="297"
      y="235"
      :valve-type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves['1067-06']"
    >
      <TagLabelInstance
        target-x="297"
        :target-width="MANUAL_VALVE_WIDTH"
        y="219"
        :tag-id="manualValves['1067-06'].tooltip?.yardTag"
      />
    </ManualValveInstance>
  </LayerFilter>
</template>
