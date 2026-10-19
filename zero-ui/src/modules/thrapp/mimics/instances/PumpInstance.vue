<script setup lang="ts">
import { reactiveOmit } from "@vueuse/core";
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
const forwardedProps = reactiveOmit(props, ["registerField", "type"]);
</script>

<template>
  <MimicTooltipTrigger :data="props">
    <Pump
      v-bind="forwardedProps"
      :pump-state="pumpState"
      :state="stateWithAlarms"
    />
    <slot />
  </MimicTooltipTrigger>
</template>
