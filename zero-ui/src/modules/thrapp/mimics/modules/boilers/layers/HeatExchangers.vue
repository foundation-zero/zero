<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrs/types";
import { ComponentOrientation } from "../../../components";
import { HeatExchangerPortOrientation } from "../../../components/heat-exchanger";
import { HeatExchangerInstance } from "../../../instances";
import { getField } from "../../../providers";
</script>

<template>
  <g>
    <HeatExchangerInstance
      x="33"
      y="435"
      tag-id="1007"
      :heat-exchanger="
        getField(SensorComponentType.HeatExchanger, 'boilers', 'boilersConsumersExchanger')
      "
      :orientation="ComponentOrientation.Down"
      :side-a="HeatExchangerPortOrientation.Side"
      :side-b="HeatExchangerPortOrientation.Top"
    />
    <HeatExchangerInstance
      x="718.5"
      y="641"
      tag-id="1009"
      :heat-exchanger="
        getField(SensorComponentType.HeatExchanger, 'boilers', 'boilersLt1Exchanger')
      "
      :orientation="ComponentOrientation.Down"
      :side-a="HeatExchangerPortOrientation.Side"
      :side-b="HeatExchangerPortOrientation.Top"
    />

    <HeatExchangerInstance
      x="470"
      y="480.5"
      tag-id="1008"
      :heat-exchanger="
        getField(SensorComponentType.HeatExchanger, 'boilers', 'boilersLt2Exchanger')
      "
      :orientation="ComponentOrientation.Down"
      :side-a="HeatExchangerPortOrientation.Side"
      :side-b="HeatExchangerPortOrientation.Top"
    />
    <HeatExchangerInstance
      x="964.5"
      y="480.5"
      tag-id="1004"
      :heat-exchanger="
        getField(SensorComponentType.HeatExchanger, 'boilers', 'boilersFahrenheitExchanger')
      "
      :orientation="ComponentOrientation.Down"
      :side-a="HeatExchangerPortOrientation.Side"
      :side-b="HeatExchangerPortOrientation.Top"
    />
  </g>
</template>
