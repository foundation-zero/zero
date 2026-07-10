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
      x="972"
      y="392"
      tag-id="1002"
      :orientation="ComponentOrientation.Right"
      :source="getField(SensorComponentType.HeatExchanger, 'pvt', 'pvtMixExchanger')"
      :controls="{}"
      :controller-state="{}"
      :parameters="{}"
      :custom="{
        sideA: HeatExchangerPortOrientation.Top,
        sideB: HeatExchangerPortOrientation.Side,
      }"
      :sensors="{
        incoming: getField(SensorComponentType.Temperature, 'pvt', 'pvtTemperatureSupply'),
        outgoing: getField(SensorComponentType.Temperature, 'pvt', 'pvtTemperatureOwnersReturn'),
        flow: getField(SensorComponentType.Flow, 'pvt', 'pvtFlowMainFwdRecovery'),
      }"
      :tooltip="{
        title: 'Heat exchanger',
        itemName: 'Main heat exchanger',
        yardTag: '1002',
        technicalName: 'pvt-heat-exchanger-main',
      }"
    />
  </g>
</template>
