<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import PressureSensor from "../components/pressure-sensor/PressureSensor.vue";
import { getMimicDataProvider } from "../providers";
const props = defineProps<MimicComponentInstanceProps>();

const { getComponentState } = getMimicDataProvider();
const state = getComponentState();
</script>

<template>
  <PressureSensor
    v-bind="props"
    :state="state"
  />
</template>
