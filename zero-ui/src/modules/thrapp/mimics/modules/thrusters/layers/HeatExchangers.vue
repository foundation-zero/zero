<script setup lang="ts">
import { MimicComponentType } from "@/modules/thrapp/types";
import { ComponentOrientation } from "../../../components";
import { PIPE_HEAT_EXCHANGER_WIDTH } from "../../../components/pipe-heat-exchanger";
import { HeatExchangerLabelInstance, PipeHeatExchangerInstance } from "../../../instances";
import { THRUSTERS_MIMIC_DATA } from "../data";

const heatExchangers = THRUSTERS_MIMIC_DATA[MimicComponentType.HeatExchanger];
</script>

<template>
  <g>
    <PipeHeatExchangerInstance
      x="664"
      y="141"
      :orientation="ComponentOrientation.Left"
      v-bind="heatExchangers['1001']"
    >
      <HeatExchangerLabelInstance
        :target-x="664"
        :target-width="PIPE_HEAT_EXCHANGER_WIDTH"
        y="192"
        :tag-id="heatExchangers['1001'].tooltip?.yardTag"
        :heat-exchanger="heatExchangers['1001'].source"
      />
    </PipeHeatExchangerInstance>
  </g>
</template>
