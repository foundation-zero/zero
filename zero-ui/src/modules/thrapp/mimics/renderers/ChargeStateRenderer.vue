<script setup lang="ts">
import { PcmChargeStatus } from "@/modules/thrsim/types";
import { computed, toRef } from "vue";
import { FieldRendererProps } from ".";
import { ChargeState, PcmChargeState } from "../components/pcm";
import { getFieldValue } from "../providers";

const props = defineProps<FieldRendererProps<PcmChargeStatus>>();

const value = getFieldValue(toRef(props, "value"));

const chargeStateByStatus: Record<PcmChargeStatus, ChargeState> = {
  [PcmChargeStatus.Full]: ChargeState.Full,
  [PcmChargeStatus.Empty]: ChargeState.Empty,
  [PcmChargeStatus.Intermediate]: ChargeState.HalfFull,
  [PcmChargeStatus.Unknown]: ChargeState.Unknown,
};

const state = computed<ChargeState | undefined>(() => {
  if (value.value === undefined) return undefined;
  return chargeStateByStatus[value.value];
});
</script>

<template>
  <PcmChargeState :state="state">
    <slot />
  </PcmChargeState>
</template>
