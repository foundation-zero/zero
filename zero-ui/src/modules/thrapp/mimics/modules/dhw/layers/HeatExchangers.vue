<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { HeatExchangerInstance, HeatExchangerLabelInstance } from "../../../instances";
import { DHW_MIMIC_DATA } from "../data";

const heatExchangers = DHW_MIMIC_DATA[MimicComponentType.HeatExchanger];
</script>

<template>
  <HeatExchangerInstance
    x="33"
    y="435"
    tag-id="1007"
    v-bind="heatExchangers['1007']"
    :orientation="ComponentOrientation.Down"
  >
    <HeatExchangerLabelInstance
      x="23"
      y="379.3"
      tag-id="1007"
      :heat-exchanger="heatExchangers['1007'].source"
    />
  </HeatExchangerInstance>
  <HeatExchangerInstance
    x="718.5"
    y="641"
    tag-id="1009"
    v-bind="heatExchangers['1009']"
    :orientation="ComponentOrientation.Down"
  >
    <HeatExchangerLabelInstance
      x="710"
      y="585"
      tag-id="1009"
      :heat-exchanger="heatExchangers['1009'].source"
    />
  </HeatExchangerInstance>

  <HeatExchangerInstance
    x="470"
    y="480.5"
    tag-id="1008"
    v-bind="heatExchangers['1008']"
    :orientation="ComponentOrientation.Down"
  >
    <HeatExchangerLabelInstance
      x="460"
      y="425"
      tag-id="1008"
      :heat-exchanger="heatExchangers['1008'].source"
    />
  </HeatExchangerInstance>
  <HeatExchangerInstance
    x="964.5"
    y="480.5"
    tag-id="1004"
    v-bind="heatExchangers['1004']"
    :orientation="ComponentOrientation.Down"
  >
    <HeatExchangerLabelInstance
      x="955"
      y="425"
      tag-id="1004"
      :heat-exchanger="heatExchangers['1004'].source"
    />
  </HeatExchangerInstance>
</template>
