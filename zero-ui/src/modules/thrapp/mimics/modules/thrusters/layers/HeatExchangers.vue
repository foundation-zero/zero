<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PIPE_HEAT_EXCHANGER_WIDTH } from "../../../components/pipe-heat-exchanger";
import { getTooltipContexts } from "../../../data";
import { HeatExchangerInstance, HeatExchangerLabelInstance } from "../../../instances";

const heatExchangers = getTooltipContexts(MimicComponentType.HeatExchanger, ["1001"]);
</script>

<template>
  <g>
    <HeatExchangerInstance
      x="664"
      y="126"
      :orientation="ComponentOrientation.Up"
      v-bind="heatExchangers['1001']"
    >
      <HeatExchangerLabelInstance
        :target-x="664"
        :target-width="PIPE_HEAT_EXCHANGER_WIDTH"
        y="192"
        :tag-id="heatExchangers['1001'].tooltip?.yardTag"
        :heat-exchanger="heatExchangers['1001'].source"
      />
    </HeatExchangerInstance>
  </g>
</template>
