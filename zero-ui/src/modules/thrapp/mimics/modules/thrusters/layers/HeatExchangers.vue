<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { HeatExchangerLabelInstance, PipeHeatExchangerInstance } from "../../../instances";
import { THRUSTERS_MIMIC_DATA } from "../data";

const heatExchangers = THRUSTERS_MIMIC_DATA[MimicComponentType.HeatExchanger];
</script>

<template>
  <g>
    <PipeHeatExchangerInstance
      x="664"
      y="141"
      :orientation="ComponentOrientation.Left"
      v-bind="heatExchangers['1001']"
    >
      <HeatExchangerLabelInstance
        x="649"
        y="185"
        :tag-id="heatExchangers['1001'].tooltip?.yardTag"
        :heat-exchanger="heatExchangers['1001'].source"
      />
    </PipeHeatExchangerInstance>
  </g>
</template>
