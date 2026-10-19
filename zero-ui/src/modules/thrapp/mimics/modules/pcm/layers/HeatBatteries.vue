<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { PcmLayout } from "../../../components/pcm";
import { getTooltipContexts } from "../../../data";
import PcmInstance from "../../../instances/PcmInstance.vue";

const heatBatteries = getTooltipContexts(MimicComponentType.Pcm, ["1049", "1050", "1051", "1052"]);
</script>

<template>
  <PcmInstance
    x="660"
    y="18.25"
    :layout="PcmLayout.LeftRight"
    heat-power="+5 kW"
    stored-energy="est. 250 kWh"
    v-bind="heatBatteries['1049']"
  />
  <PcmInstance
    x="660"
    y="214.25"
    heat-power="+5 kW"
    stored-energy="est. 250 kWh"
    v-bind="heatBatteries['1050']"
  />
  <PcmInstance
    x="660"
    y="410.5"
    heat-power="+5 kW"
    stored-energy="est. 250 kWh"
    v-bind="heatBatteries['1051']"
  />
  <PcmInstance
    x="660"
    y="607.8"
    heat-power="+5 kW"
    stored-energy="est. 250 kWh"
    v-bind="heatBatteries['1052']"
  />
</template>
