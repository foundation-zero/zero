<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import TemperatureSensor from "../components/temperature-sensor/TemperatureSensor.vue";
import { getMimicDataProvider } from "../providers";

const props = defineProps<MimicComponentInstanceProps>();

const { getComponentState } = getMimicDataProvider();
const state = getComponentState();
</script>

<template>
  <TemperatureSensor
    v-bind="props"
    :state="state"
  />
</template>
