<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { getTooltipContexts } from "../../../data";
import { HeatExchangerInstance, HeatExchangerLabelInstance } from "../../../instances";

const heatExchangers = getTooltipContexts(MimicComponentType.HeatExchanger, [
  "1004",
  "1005",
  "1003",
]);
</script>

<template>
  <g>
    <HeatExchangerInstance
      x="25"
      y="314"
      :orientation="ComponentOrientation.Right"
      v-bind="heatExchangers['1004']"
    >
      <HeatExchangerLabelInstance
        x="86"
        y="307"
        :tag-id="heatExchangers['1004'].tooltip?.yardTag"
        :heat-exchanger="heatExchangers['1004'].source"
      />
    </HeatExchangerInstance>
    <HeatExchangerInstance
      x="439.2"
      y="471"
      :orientation="ComponentOrientation.Down"
      v-bind="heatExchangers['1005']"
    >
      <HeatExchangerLabelInstance
        x="424.2"
        y="400"
        :tag-id="heatExchangers['1005'].tooltip?.yardTag"
        :heat-exchanger="heatExchangers['1005'].source"
      />
    </HeatExchangerInstance>
    <HeatExchangerInstance
      x="1508.35"
      y="179"
      :orientation="ComponentOrientation.Right"
      v-bind="heatExchangers['1003']"
    >
      <HeatExchangerLabelInstance
        x="1564"
        y="163.5"
        :tag-id="heatExchangers['1003'].tooltip?.yardTag"
        :heat-exchanger="heatExchangers['1003'].source"
      />
    </HeatExchangerInstance>
  </g>
</template>
