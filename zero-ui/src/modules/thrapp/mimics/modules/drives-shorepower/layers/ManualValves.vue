<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import LayerFilter from "../../../components/layer-filter/LayerFilter.vue";
import { LayerFilterOption } from "../../../components/layer-filter/layer-filter.provider";
import { ManualValveType } from "../../../components/manual-valve";
import { getTooltipContexts } from "../../../data";
import { ManualValveInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";

const manualValves = getTooltipContexts(MimicComponentType.ManualValve, [
  "1080-05",
  "1080-04",
  "1080-03",
  "1080-02",
]);
</script>

<template>
  <LayerFilter :filter="LayerFilterOption.ManualComponents">
    <ManualValveInstance
      x="335.63"
      y="109.41"
      :valve-type="ManualValveType.Flow"
      :orientation="ComponentOrientation.Right"
      v-bind="manualValves['1080-05']"
    >
      <TagLabelInstance
        x="370.63"
        y="112.41"
        :tag-id="manualValves['1080-05'].tooltip?.yardTag"
      />
    </ManualValveInstance>
    <ManualValveInstance
      x="335.63"
      y="322.82"
      :valve-type="ManualValveType.Flow"
      :orientation="ComponentOrientation.Right"
      v-bind="manualValves['1080-04']"
    >
      <TagLabelInstance
        x="370.63"
        y="326.41"
        :tag-id="manualValves['1080-04'].tooltip?.yardTag"
      />
    </ManualValveInstance>
    <ManualValveInstance
      x="335.63"
      y="531.82"
      :valve-type="ManualValveType.Flow"
      :orientation="ComponentOrientation.Right"
      v-bind="manualValves['1080-03']"
    >
      <TagLabelInstance
        x="370.63"
        y="534.41"
        :tag-id="manualValves['1080-03'].tooltip?.yardTag"
      />
    </ManualValveInstance>
    <ManualValveInstance
      x="335.63"
      y="728.82"
      :valve-type="ManualValveType.Flow"
      :orientation="ComponentOrientation.Right"
      v-bind="manualValves['1080-02']"
    >
      <TagLabelInstance
        x="370.63"
        y="733.41"
        :tag-id="manualValves['1080-02'].tooltip?.yardTag"
      />
    </ManualValveInstance>
  </LayerFilter>
</template>
