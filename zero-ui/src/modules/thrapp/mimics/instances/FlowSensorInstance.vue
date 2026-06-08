<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import FlowSensor from "../components/flow-sensor/FlowSensor.vue";
import { getMimicDataProvider } from "../providers";

const props = defineProps<MimicComponentInstanceProps>();

const { getComponentState } = getMimicDataProvider();
const state = getComponentState();
</script>

<template>
  <FlowSensor
    v-bind="props"
    :state="state"
  />
</template>
