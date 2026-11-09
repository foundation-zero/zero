<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PRESSURE_GAUGE_WIDTH } from "../../../components/pressure-gauge";
import { getTooltipContexts } from "../../../data";
import { PressureGaugeInstance, TagLabelInstance } from "../../../instances";
import LayerFilter from "../../../components/layer-filter/LayerFilter.vue";
import { LayerFilterOption } from "../../../components/layer-filter/layer-filter.provider";

const pressureGauges = getTooltipContexts(MimicComponentType.PressureGauge, ["1096-05", "1095-13"]);
</script>

<template>
  <LayerFilter :filter="LayerFilterOption.ManualComponents">
    <PressureGaugeInstance
      x="1232"
      y="579.916"
      :orientation="ComponentOrientation.Down"
      v-bind="pressureGauges['1095-13']"
    >
      <TagLabelInstance
        target-x="1232"
        :target-width="PRESSURE_GAUGE_WIDTH"
        y="618"
        :tag-id="pressureGauges['1095-13'].tooltip?.yardTag"
      />
    </PressureGaugeInstance>
  </LayerFilter>
  <LayerFilter :filter="LayerFilterOption.SupportComponents">
    <PressureGaugeInstance
      x="1671"
      y="158.5"
      :orientation="ComponentOrientation.Right"
      v-bind="pressureGauges['1096-05']"
    >
      <TagLabelInstance
        x="1621"
        y="160"
        :tag-id="pressureGauges['1096-05'].tooltip?.yardTag"
      />
    </PressureGaugeInstance>
  </LayerFilter>
</template>
