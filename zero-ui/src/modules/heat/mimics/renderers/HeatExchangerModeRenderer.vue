<script setup lang="ts">
import { computed, toRef } from "vue";
import { FieldRendererProps } from ".";
import HeatExchangerMode from "../components/heat-exchanger/HeatExchangerMode.vue";
import { HeatingState } from "../components/index.ts";
import { getFieldValue } from "../providers";

const props = defineProps<FieldRendererProps<number>>();

const value = getFieldValue(toRef(props, "value"));

const state = computed<HeatingState>(() => {
  if (value.value === undefined || value.value === 0) return HeatingState.Idle;
  else if (value.value > 0) return HeatingState.HeatingMedium;
  else return HeatingState.CoolingMedium;
});
</script>

<template>
  <HeatExchangerMode :state="state" />
</template>
