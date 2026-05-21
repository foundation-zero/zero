<script setup lang="ts">
import { ComponentOrientation } from "../../../components";
import { HeatExchangerPortOrientation } from "../../../components/heat-exchanger";
import { HeatExchangerInstance } from "../../../instances";
</script>

<template>
  <g>
    <HeatExchangerInstance
      x="33"
      y="435"
      tag-id="1007"
      :orientation="ComponentOrientation.Down"
      :side-a="HeatExchangerPortOrientation.Side"
      :side-b="HeatExchangerPortOrientation.Top"
    />
    <HeatExchangerInstance
      x="718.5"
      y="641"
      tag-id="1009"
      :orientation="ComponentOrientation.Down"
      :side-a="HeatExchangerPortOrientation.Side"
      :side-b="HeatExchangerPortOrientation.Top"
    />

    <HeatExchangerInstance
      x="470"
      y="480.5"
      tag-id="1008"
      :orientation="ComponentOrientation.Down"
      :side-a="HeatExchangerPortOrientation.Side"
      :side-b="HeatExchangerPortOrientation.Top"
    />
    <HeatExchangerInstance
      x="964.5"
      y="480.5"
      tag-id="1004"
      :orientation="ComponentOrientation.Down"
      :side-a="HeatExchangerPortOrientation.Side"
      :side-b="HeatExchangerPortOrientation.Top"
    />
  </g>
</template>
