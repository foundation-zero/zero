<script setup lang="ts">
import { computed } from "vue";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { PumpState } from "../components/pump";
import Pump from "../components/pump/Pump.vue";
import { getMimicDataProvider } from "../providers";

const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.Pump>
>();

const { getSensorValue, getComponentState } = getMimicDataProvider();
const pump = getSensorValue(props.source);
const state = getComponentState();

const pumpState = computed(() => {
  if (pump.value?.flow.value != undefined && pump.value?.flow.value > 0) return PumpState.Active;
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
      :state="state"
    />
  </MimicTooltipTrigger>
</template>
