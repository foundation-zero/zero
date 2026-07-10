<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import PressureGauge from "../components/pressure-gauge/PressureGauge.vue";
import { getMimicDataProvider } from "../providers";
const props = defineProps<MimicComponentInstanceProps>();

const { getComponentState } = getMimicDataProvider();
const state = getComponentState();
</script>

<template>
  <PressureGauge
    v-bind="props"
    :state="state"
  />
</template>
