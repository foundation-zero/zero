<script setup lang="ts">
import { computed } from "vue";
import { MimicComponentInstanceProps } from ".";

import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { PipeHeatExchangerState } from "../components/pipe-heat-exchanger";
import PipeHeatExchanger from "../components/pipe-heat-exchanger/PipeHeatExchanger.vue";
import { getMimicDataProvider } from "../providers";

const props = withDefaults(
  defineProps<
    MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.HeatExchanger>
  >(),
  {},
);

const { getSensorValue } = getMimicDataProvider();

const heatExchanger = getSensorValue(props.source);

const state = computed<PipeHeatExchangerState>(() => {
  if (heatExchanger.value?.heat.value === undefined || heatExchanger.value?.heat.value === 0)
    return PipeHeatExchangerState.Idle;
  else if (heatExchanger.value.heat.value > 0) return PipeHeatExchangerState.Heating;
  else return PipeHeatExchangerState.Cooling;
});
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.HeatExchanger"
    :data="props"
  >
    <PipeHeatExchanger
      v-bind="props"
      :pump-state="state"
    />
    <slot />
  </MimicTooltipTrigger>
</template>
