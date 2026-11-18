<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import LayerFilter from "../../../components/layer-filter/LayerFilter.vue";
import { LayerFilterOption } from "../../../components/layer-filter/layer-filter.provider";
import { MANUAL_VALVE_WIDTH, ManualValveType } from "../../../components/manual-valve";
import { getTooltipContexts } from "../../../data";
import { ManualValveInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";

const manualValves = getTooltipContexts(MimicComponentType.ManualValve, [
  "1067-04",
  "1067-03",
  "1067-02",
  "1067-01",
]);
</script>

<template>
  <LayerFilter :filter="LayerFilterOption.ManualComponents">
    <ManualValveInstance
      x="299"
      y="21"
      :valve-type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves['1067-04']"
    >
      <TagLabelInstance
        target-x="299"
        :target-width="MANUAL_VALVE_WIDTH"
        y="3"
        :tag-id="manualValves['1067-04'].tooltip?.yardTag"
      />
    </ManualValveInstance>
    <ManualValveInstance
      x="299"
      y="235"
      :valve-type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves['1067-03']"
    >
      <TagLabelInstance
        target-x="299"
        :target-width="MANUAL_VALVE_WIDTH"
        y="219"
        :tag-id="manualValves['1067-03'].tooltip?.yardTag"
      />
    </ManualValveInstance>
    <ManualValveInstance
      x="299"
      y="443"
      :valve-type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves['1067-02']"
    >
      <TagLabelInstance
        target-x="299"
        :target-width="MANUAL_VALVE_WIDTH"
        y="430"
        :tag-id="manualValves['1067-02'].tooltip?.yardTag"
      />
    </ManualValveInstance>
    <ManualValveInstance
      x="299"
      y="637"
      :valve-type="ManualValveType.Switch"
      :orientation="ComponentOrientation.Up"
      v-bind="manualValves['1067-01']"
    >
      <TagLabelInstance
        target-x="299"
        :target-width="MANUAL_VALVE_WIDTH"
        y="625"
        :tag-id="manualValves['1067-01'].tooltip?.yardTag"
      />
    </ManualValveInstance>
  </LayerFilter>
</template>
