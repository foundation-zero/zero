<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { HeatExchangerInstance } from "../../../instances";
import { BOILERS_MIMIC_DATA } from "../data";

const heatExchangers = BOILERS_MIMIC_DATA[MimicComponentType.HeatExchanger];
</script>

<template>
  <HeatExchangerInstance
    x="33"
    y="435"
    tag-id="1007"
    v-bind="heatExchangers['1007']"
    :orientation="ComponentOrientation.Down"
  />
  <HeatExchangerInstance
    x="718.5"
    y="641"
    tag-id="1009"
    v-bind="heatExchangers['1009']"
    :orientation="ComponentOrientation.Down"
  />

  <HeatExchangerInstance
    x="470"
    y="480.5"
    tag-id="1008"
    v-bind="heatExchangers['1008']"
    :orientation="ComponentOrientation.Down"
  />
  <HeatExchangerInstance
    x="964.5"
    y="480.5"
    tag-id="1004"
    v-bind="heatExchangers['1004']"
    :orientation="ComponentOrientation.Down"
  />
</template>
