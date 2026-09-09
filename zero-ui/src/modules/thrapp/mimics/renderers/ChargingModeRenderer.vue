<script setup lang="ts">
import { computed, toRef } from "vue";
import { FieldRendererProps } from ".";
import { ChargingMode, PcmChargingMode } from "../components/pcm";
import { getFieldValue } from "../providers";

const props = defineProps<FieldRendererProps<number>>();

const value = getFieldValue(toRef(props, "value"));

const mode = computed<ChargingMode | undefined>(() => {
  if (value.value === undefined) return undefined;
  else if (value.value === 0) return ChargingMode.Idle;
  else if (value.value > 0) return ChargingMode.Charging;
  else return ChargingMode.Discharging;
});
</script>

<template>
  <PcmChargingMode :mode="mode">
    <slot />
  </PcmChargingMode>
</template>
