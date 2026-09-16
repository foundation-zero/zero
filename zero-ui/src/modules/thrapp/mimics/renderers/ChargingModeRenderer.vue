<script setup lang="ts">
import { PcmChargingState } from "@/modules/thrsim/types";
import { computed, toRef } from "vue";
import { FieldRendererProps } from ".";
import { ChargingMode, PcmChargingMode } from "../components/pcm";
import { getFieldValue } from "../providers";

const props = defineProps<FieldRendererProps<PcmChargingState>>();

const value = getFieldValue(toRef(props, "value"));

const chargingModeByState: Record<PcmChargingState, ChargingMode> = {
  [PcmChargingState.Charging]: ChargingMode.Charging,
  [PcmChargingState.Discharging]: ChargingMode.Discharging,
  [PcmChargingState.Idle]: ChargingMode.Idle,
};

const mode = computed<ChargingMode | undefined>(() => {
  if (value.value === undefined) return undefined;
  return chargingModeByState[value.value];
});
</script>

<template>
  <PcmChargingMode :mode="mode">
    <slot />
  </PcmChargingMode>
</template>
