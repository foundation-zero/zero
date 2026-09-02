<script setup lang="ts">
import { reactiveOmit } from "@vueuse/core";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types/index.ts";

import ActuatedValve from "../components/actuated-valve/ActuatedValve.vue";
import { ThreeWayValveLegs } from "../components/actuated-valve/index.ts";
import MixValve from "../components/actuated-valve/MixValve.vue";
import ThreeWayValve from "../components/actuated-valve/ThreeWayValve.vue";
import { getMimicDataProvider } from "../providers/index.ts";
import { MimicComponentInstanceProps } from "./index.ts";

const props = defineProps<
  MimicComponentInstanceProps &
    TooltipComponentContext<MimicComponentType.MixValve> & { legs?: ThreeWayValveLegs }
>();

const { getSensorValue, getComponentState } = getMimicDataProvider();
const valve = getSensorValue(props.source);
const state = getComponentState();
const forwardedProps = reactiveOmit(props, ["legs"]);
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.MixValve"
    :data="forwardedProps"
  >
    <ActuatedValve
      v-bind="forwardedProps"
      :state="state"
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
