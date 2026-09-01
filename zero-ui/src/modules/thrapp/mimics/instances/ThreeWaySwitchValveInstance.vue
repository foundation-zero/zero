<script setup lang="ts">
import { computed } from "vue";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import ActuatedValve from "../components/actuated-valve/ActuatedValve.vue";
import { ThreeWayValveLegs } from "../components/actuated-valve/index.ts";
import SwitchValve from "../components/actuated-valve/SwitchValve.vue";
import ThreeWayValve from "../components/actuated-valve/ThreeWayValve.vue";
import { getMimicDataProvider } from "../providers/index.ts";
import { MimicComponentInstanceProps } from "./index.ts";

const props = defineProps<
  MimicComponentInstanceProps &
    TooltipComponentContext<MimicComponentType.ThreeWaySwitchValve> & {
      legs?: ThreeWayValveLegs;
    }
>();

const { getSensorValue, getComponentState } = getMimicDataProvider();
const valve = getSensorValue(props.source);
const state = getComponentState();

// A switch valve is either fully on A or fully on B, never partially mixed.
const flow = computed(() => Math.round(valve.value?.positionRel.value ?? 0));
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.ThreeWaySwitchValve"
    :data="props"
  >
    <ActuatedValve
      v-bind="props"
      :state="state"
    >
      <SwitchValve />
      <ThreeWayValve
        :flow="flow"
        :legs="legs"
      />
    </ActuatedValve>
    <slot />
  </MimicTooltipTrigger>
</template>
