<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PipeHeatExchangerInstance } from "../../../instances";
import HeatExchangerLabelInstance from "../../../instances/HeatExchangerLabelInstance.vue";
import { PVT_MIMIC_DATA } from "../data";

const heatExchangers = PVT_MIMIC_DATA[MimicComponentType.HeatExchanger];
</script>

<template>
  <g>
    <PipeHeatExchangerInstance
      x="1037"
      y="382"
      :orientation="ComponentOrientation.Up"
      v-bind="heatExchangers['1002']"
    >
      <HeatExchangerLabelInstance
        x="952"
        y="372"
        :tag-id="heatExchangers['1002'].tooltip?.yardTag"
        :heat-exchanger="heatExchangers['1002'].source"
      />
    </PipeHeatExchangerInstance>
  </g>
</template>
