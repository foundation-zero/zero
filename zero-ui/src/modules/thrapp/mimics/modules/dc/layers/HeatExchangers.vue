<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { HEAT_EXCHANGER_WIDTH } from "../../../components/heat-exchanger";
import { HeatExchangerInstance, HeatExchangerLabelInstance } from "../../../instances";
import { DC_HEAT_EXCHANGER_DATA } from "../data";

const heatExchangers = DC_HEAT_EXCHANGER_DATA[MimicComponentType.HeatExchanger];
</script>

<template>
  <HeatExchangerInstance
    x="885.1406"
    y="490.9006"
    :orientation="ComponentOrientation.Down"
    v-bind="heatExchangers['1006']"
  >
    <HeatExchangerLabelInstance
      target-x="885.1406"
      :target-width="HEAT_EXCHANGER_WIDTH"
      y="430.9006"
      :tag-id="heatExchangers['1006'].tooltip?.yardTag"
      :heat-exchanger="heatExchangers['1006'].source"
    />
  </HeatExchangerInstance>
  <HeatExchangerInstance
    x="1246.1406"
    y="333.1458"
    :orientation="ComponentOrientation.Right"
    v-bind="heatExchangers['1008']"
  >
    <HeatExchangerLabelInstance
      x="1308.1406"
      y="323.1458"
      :tag-id="heatExchangers['1008'].tooltip?.yardTag"
      :heat-exchanger="heatExchangers['1008'].source"
    />
  </HeatExchangerInstance>
</template>
