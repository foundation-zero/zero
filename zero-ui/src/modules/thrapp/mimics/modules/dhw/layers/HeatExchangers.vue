<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { HEAT_EXCHANGER_WIDTH } from "../../../components/heat-exchanger";
import { HeatExchangerInstance, HeatExchangerLabelInstance } from "../../../instances";
import { DHW_MIMIC_DATA } from "../data";

const heatExchangers = DHW_MIMIC_DATA[MimicComponentType.HeatExchanger];
</script>

<template>
  <HeatExchangerInstance
    x="33"
    y="435"
    v-bind="heatExchangers['1007']"
    :orientation="ComponentOrientation.Down"
  >
    <HeatExchangerLabelInstance
      :target-x="33"
      :target-width="HEAT_EXCHANGER_WIDTH"
      y="379.3"
      :tag-id="heatExchangers['1007'].tooltip?.yardTag"
      :heat-exchanger="heatExchangers['1007'].source"
    />
  </HeatExchangerInstance>
  <HeatExchangerInstance
    x="718.5"
    y="641"
    v-bind="heatExchangers['1009']"
    :orientation="ComponentOrientation.Down"
  >
    <HeatExchangerLabelInstance
      :target-x="718.5"
      :target-width="HEAT_EXCHANGER_WIDTH"
      y="585"
      :tag-id="heatExchangers['1009'].tooltip?.yardTag"
      :heat-exchanger="heatExchangers['1009'].source"
    />
  </HeatExchangerInstance>

  <HeatExchangerInstance
    x="470"
    y="480.5"
    v-bind="heatExchangers['1008']"
    :orientation="ComponentOrientation.Down"
  >
    <HeatExchangerLabelInstance
      :target-x="470"
      :target-width="HEAT_EXCHANGER_WIDTH"
      y="425"
      :tag-id="heatExchangers['1008'].tooltip?.yardTag"
      :heat-exchanger="heatExchangers['1008'].source"
    />
  </HeatExchangerInstance>
  <HeatExchangerInstance
    x="964.5"
    y="480.5"
    v-bind="heatExchangers['1004']"
    :orientation="ComponentOrientation.Down"
  >
    <HeatExchangerLabelInstance
      :target-x="964.5"
      :target-width="HEAT_EXCHANGER_WIDTH"
      y="425"
      :tag-id="heatExchangers['1004'].tooltip?.yardTag"
      :heat-exchanger="heatExchangers['1004'].source"
    />
  </HeatExchangerInstance>
</template>
