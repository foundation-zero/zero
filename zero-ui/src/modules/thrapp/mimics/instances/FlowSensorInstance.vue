<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import FlowSensor from "../components/flow-sensor/FlowSensor.vue";

const props = defineProps<MimicComponentInstanceProps>();
</script>

<template>
  <FlowSensor v-bind="props" />
</template>
