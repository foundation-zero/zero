<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { getTooltipContexts } from "../../../data";
import { PressureGaugeInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";
import LayerFilter from "../../../components/layer-filter/LayerFilter.vue";
import { LayerFilterOption } from "../../../components/layer-filter/layer-filter.provider";

const manualPressureSensors = getTooltipContexts(MimicComponentType.PressureGauge, ["1095-14"]);
</script>

<template>
  <LayerFilter :filter="LayerFilterOption.ManualComponents">
    <PressureGaugeInstance
      x="197"
      y="423.2099609375"
      :orientation="ComponentOrientation.Left"
      v-bind="manualPressureSensors['1095-14']"
    >
      <TagLabelInstance
        x="236"
        y="425"
        :tag-id="manualPressureSensors['1095-14'].tooltip?.yardTag"
      />
    </PressureGaugeInstance>
  </LayerFilter>
</template>
