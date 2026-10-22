<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { HEAT_EXCHANGER_WIDTH } from "../../../components/heat-exchanger";
import { getTooltipContexts } from "../../../data";
import { HeatExchangerInstance, HeatExchangerLabelInstance } from "../../../instances";

const heatExchangers = {
  ...getTooltipContexts(MimicComponentType.HeatExchanger, ["1011"]),
  ...getTooltipContexts(MimicComponentType.HeatExchanger, ["1009"], 1),
};
</script>

<template>
  <g>
    <HeatExchangerInstance
      x="1106.0713"
      y="686"
      :orientation="ComponentOrientation.Down"
      v-bind="heatExchangers['1011']"
    >
      <HeatExchangerLabelInstance
        target-x="1106.0713"
        :target-width="HEAT_EXCHANGER_WIDTH"
        y="626.416"
        :tag-id="heatExchangers['1011'].tooltip?.yardTag"
        :heat-exchanger="heatExchangers['1011'].source"
      />
    </HeatExchangerInstance>
    <HeatExchangerInstance
      x="1382.418"
      y="318.916"
      :orientation="ComponentOrientation.Right"
      v-bind="heatExchangers['1009']"
    >
      <HeatExchangerLabelInstance
        target-x="1382.418"
        :target-width="HEAT_EXCHANGER_WIDTH"
        y="259.416"
        :tag-id="heatExchangers['1009'].tooltip?.yardTag"
        :heat-exchanger="heatExchangers['1009'].source"
      />
    </HeatExchangerInstance>
  </g>
</template>
