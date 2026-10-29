<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { getTooltipContexts } from "../../../data";
import { HeatExchangerInstance } from "../../../instances";
import HeatExchangerLabelInstance from "../../../instances/HeatExchangerLabelInstance.vue";

const heatExchangers = getTooltipContexts(MimicComponentType.HeatExchanger, ["1002"]);
</script>

<template>
  <g>
    <HeatExchangerInstance
      x="1048"
      y="375"
      :orientation="ComponentOrientation.Right"
      v-bind="heatExchangers['1002']"
    >
      <HeatExchangerLabelInstance
        x="959"
        y="366"
        :tag-id="heatExchangers['1002'].tooltip?.yardTag"
        :heat-exchanger="heatExchangers['1002'].source"
      />
    </HeatExchangerInstance>
  </g>
</template>
