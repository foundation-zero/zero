<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { HeatExchangerInstance, HeatExchangerLabelInstance } from "../../../instances";
import { PCM_MIMIC_DATA } from "../data";

const heatExchangers = PCM_MIMIC_DATA[MimicComponentType.HeatExchanger];
</script>

<template>
  <HeatExchangerInstance
    x="1124"
    y="300"
    :orientation="ComponentOrientation.Right"
    v-bind="heatExchangers['1007']"
  >
    <HeatExchangerLabelInstance
      :target-x="1104"
      y="292"
      :tag-id="heatExchangers['1007'].tooltip?.yardTag"
      :heat-exchanger="heatExchangers['1007'].source"
    />
  </HeatExchangerInstance>
  <HeatExchangerInstance
    x="1248"
    y="466.5"
    :orientation="ComponentOrientation.Right"
    v-bind="heatExchangers['1004']"
  >
    <HeatExchangerLabelInstance
      :target-x="1228"
      y="460"
      :tag-id="heatExchangers['1004'].tooltip?.yardTag"
      :heat-exchanger="heatExchangers['1004'].source"
    />
  </HeatExchangerInstance>
</template>
