<script setup lang="ts">
import { computed, toRef } from "vue";
import { FieldRendererProps } from ".";
import { ChargeState, PcmChargeState } from "../components/pcm";
import { getFieldValue } from "../providers";

const props = defineProps<FieldRendererProps<number>>();

const value = getFieldValue(toRef(props, "value"));

const state = computed<ChargeState | undefined>(() => {
  if (value.value === undefined) return undefined;
  else if (value.value <= 0) return ChargeState.Empty;
  else if (value.value >= 100) return ChargeState.Full;
  else return ChargeState.HalfFull;
});
</script>

<template>
  <PcmChargeState :state="state">
    <slot />
  </PcmChargeState>
</template>
