<script setup lang="ts">
import { computed } from "vue";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import ActuatedValve from "../components/actuated-valve/ActuatedValve.vue";
import MixValve from "../components/actuated-valve/MixValve.vue";
import TwoWayValve from "../components/actuated-valve/TwoWayValve.vue";
import { getMimicDataProvider } from "../providers";
import { componentStateFromAlarms } from "../providers/helpers";

const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.FlowControlValve>
>();

const { getSensorValue, getComponentState } = getMimicDataProvider();
const valve = getSensorValue(props.source);
const state = getComponentState();
const stateWithAlarms = computed(() => componentStateFromAlarms(state.value, valve.value));
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.FlowControlValve"
    :data="props"
  >
    <ActuatedValve
      v-bind="props"
      :state="stateWithAlarms"
    >
      <TwoWayValve :flow="valve?.positionRel.value ?? 0" />
      <MixValve />
    </ActuatedValve>
    <slot />
  </MimicTooltipTrigger>
</template>
