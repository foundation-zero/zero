<script setup lang="ts">
import { computed } from "vue";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { PumpProps, PumpState } from "../components/pump";
import Pump from "../components/pump/Pump.vue";
import { getMimicDataProvider } from "../providers";
import { componentStateFromAlarms } from "../providers/helpers";

const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.Pump> & PumpProps
>();

const { getControlValue, getComponentState, getSensorValue } = getMimicDataProvider();
const pumpControl = getControlValue(props.controls.pump);
const pumpSensor = getSensorValue(props.source);
const state = getComponentState();
const stateWithAlarms = computed(() => componentStateFromAlarms(state.value, pumpSensor.value));

const pumpState = computed(() => {
  if (pumpControl.value?.on.value) return PumpState.Active;
  else return PumpState.Inactive;
});
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.Pump"
    :data="props"
  >
    <Pump
      v-bind="props"
      :pump-state="pumpState"
      :state="stateWithAlarms"
    />
    <slot />
  </MimicTooltipTrigger>
</template>
