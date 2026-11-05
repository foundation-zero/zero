<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PRESSURE_GAUGE_WIDTH } from "../../../components/pressure-gauge";
import { getTooltipContexts } from "../../../data";
import { PressureGaugeInstance } from "../../../instances";
import TagLabelInstance from "../../../instances/TagLabelInstance.vue";
import LayerFilter from "../../../components/layer-filter/LayerFilter.vue";
import { LayerFilterOption } from "../../../components/layer-filter/layer-filter.provider";

const manualPressureSensors = getTooltipContexts(MimicComponentType.PressureGauge, ["1095-01"]);
</script>

<template>
  <LayerFilter :filter="LayerFilterOption.ManualComponents">
    <PressureGaugeInstance
      x="518"
      y="229"
      :orientation="ComponentOrientation.Down"
      v-bind="manualPressureSensors['1095-01']"
      ><TagLabelInstance
        :target-x="518"
        :target-width="PRESSURE_GAUGE_WIDTH"
        y="213"
        :tag-id="manualPressureSensors['1095-01'].tooltip?.yardTag"
      />
    </PressureGaugeInstance>
  </LayerFilter>
</template>
