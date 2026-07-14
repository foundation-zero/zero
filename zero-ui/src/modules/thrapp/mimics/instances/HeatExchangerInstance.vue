<script setup lang="ts">
import { computed } from "vue";
import { MimicComponentInstanceProps } from ".";
import { HeatingState } from "../components";
import { HeatExchangerPortOrientation } from "../components/heat-exchanger";

import { SensorComponentType } from "@/modules/thrs/types";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import HeatExchanger from "../components/heat-exchanger/HeatExchanger.vue";
import HeatExchangerPort from "../components/heat-exchanger/HeatExchangerPort.vue";
import { getMimicDataProvider, ModuleField } from "../providers";

export type HeatExchangerInstanceProps = {
  sideA?: HeatExchangerPortOrientation;
  sideB?: HeatExchangerPortOrientation;
  heatExchanger: ModuleField<SensorComponentType.HeatExchanger>;
};

const props = withDefaults(
  defineProps<
    MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.HeatExchanger>
  >(),
  {},
);

const { getSensorValue } = getMimicDataProvider();

const heatExchanger = getSensorValue(props.source);

type HeatExchangerState = [sideA: HeatingState, sideB: HeatingState];

const portStates = computed<HeatExchangerState>(() => {
  if (heatExchanger.value?.heat.value === undefined || heatExchanger.value?.heat.value === 0)
    return [HeatingState.Idle, HeatingState.Idle];
  else if (heatExchanger.value.heat.value > 0)
    return [HeatingState.HeatingMedium, HeatingState.HeatingHigh];
  else return [HeatingState.CoolingMedium, HeatingState.CoolingHigh];
});

const exchangerState = computed(() => {
  const [portA] = portStates.value;

  if (portA === HeatingState.Idle) return HeatingState.Inactive;
  else return HeatingState.Active;
});
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.HeatExchanger"
    :data="props"
  >
    <HeatExchanger
      v-bind="props"
      :heating-state="exchangerState"
    >
      <HeatExchangerPort
        side="a"
        :state="portStates[0]"
        :orientation="custom.sideA"
      />
      <HeatExchangerPort
        side="b"
        :state="portStates[1]"
        :orientation="custom.sideB"
      />
    </HeatExchanger>
    <slot />
  </MimicTooltipTrigger>
</template>
