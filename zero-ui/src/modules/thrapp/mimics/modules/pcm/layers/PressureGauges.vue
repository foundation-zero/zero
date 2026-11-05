<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { getTooltipContexts } from "../../../data";
import { PressureGaugeInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";
import LayerFilter from "../../../components/layer-filter/LayerFilter.vue";
import { LayerFilterOption } from "../../../components/layer-filter/layer-filter.provider";

const pressureGauges = getTooltipContexts(MimicComponentType.PressureGauge, ["1095-06", "1096-09"]);
</script>

<template>
  <LayerFilter :filter="LayerFilterOption.ManualComponents">
    <PressureGaugeInstance
      x="78"
      y="130"
      :orientation="ComponentOrientation.Right"
      v-bind="pressureGauges['1095-06']"
    >
      <TagLabelInstance
        x="40"
        y="130"
        :tag-id="pressureGauges['1095-06'].tooltip?.yardTag"
      />
    </PressureGaugeInstance>
    <PressureGaugeInstance
      x="297"
      y="775"
      :orientation="ComponentOrientation.Right"
      v-bind="pressureGauges['1096-09']"
    >
      <TagLabelInstance
        :target-x="275"
        y="775"
        :tag-id="pressureGauges['1096-09'].tooltip?.yardTag"
      />
    </PressureGaugeInstance>
  </LayerFilter>
</template>
