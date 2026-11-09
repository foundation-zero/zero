<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PRESSURE_GAUGE_WIDTH } from "../../../components/pressure-gauge";
import { getTooltipContexts } from "../../../data";
import { PressureGaugeInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";
import LayerFilter from "../../../components/layer-filter/LayerFilter.vue";
import { LayerFilterOption } from "../../../components/layer-filter/layer-filter.provider";

const pressureGauges = getTooltipContexts(MimicComponentType.PressureGauge, [
  "1095-03",
  "1095-04",
  "1188-03",
]);
</script>

<template>
  <LayerFilter :filter="LayerFilterOption.ManualComponents">
    <PressureGaugeInstance
      x="391"
      y="190"
      :orientation="ComponentOrientation.Down"
      v-bind="pressureGauges['1095-03']"
    >
      <TagLabelInstance
        :target-x="391.5"
        :target-width="PRESSURE_GAUGE_WIDTH"
        y="175"
        :tag-id="pressureGauges['1095-03'].tooltip?.yardTag"
      />
    </PressureGaugeInstance>
    <PressureGaugeInstance
      x="391"
      y="387"
      :orientation="ComponentOrientation.Down"
      v-bind="pressureGauges['1095-04']"
    >
      <TagLabelInstance
        :target-x="391.5"
        :target-width="PRESSURE_GAUGE_WIDTH"
        y="370"
        :tag-id="pressureGauges['1095-04'].tooltip?.yardTag"
      />
    </PressureGaugeInstance>
    <PressureGaugeInstance
      x="391"
      y="611"
      :orientation="ComponentOrientation.Down"
      v-bind="pressureGauges['1188-03']"
    >
      <TagLabelInstance
        :target-x="392.5"
        :target-width="PRESSURE_GAUGE_WIDTH"
        y="595"
        :tag-id="pressureGauges['1188-03'].tooltip?.yardTag"
      />
    </PressureGaugeInstance>
  </LayerFilter>
</template>
