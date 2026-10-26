<script setup lang="ts">
import { reactiveOmit } from "@vueuse/core";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";

import { computed } from "vue";
import { MimicComponentInstanceProps } from ".";
import { ThreeWayValveLegs } from "../components/actuated-valve";
import ActuatedValve from "../components/actuated-valve/ActuatedValve.vue";
import MixValve from "../components/actuated-valve/MixValve.vue";
import ThreeWayValve from "../components/actuated-valve/ThreeWayValve.vue";
import { getMimicDataProvider } from "../providers";
import { componentStateFromAlarms } from "../providers/helpers";

const props = defineProps<
  MimicComponentInstanceProps &
    TooltipComponentContext<MimicComponentType.MixValve> & { legs?: ThreeWayValveLegs }
>();

const { getSensorValue, getComponentState } = getMimicDataProvider();
const valve = getSensorValue(props.source);
const state = getComponentState();
const stateWithAlarms = computed(() => componentStateFromAlarms(state.value, valve.value));
const forwardedProps = reactiveOmit(props, ["legs", "registerField", "type"]);
</script>

<template>
  <MimicTooltipTrigger :data="props">
    <ActuatedValve
      v-bind="forwardedProps"
      :state="stateWithAlarms"
    >
      <MixValve />
      <ThreeWayValve
        :flow="valve?.positionRel.value ?? 0"
        :legs="legs"
      />
    </ActuatedValve>
    <slot />
  </MimicTooltipTrigger>
</template>
