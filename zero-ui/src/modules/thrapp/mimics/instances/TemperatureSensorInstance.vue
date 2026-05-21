<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import TemperatureSensor from "../components/temperature-sensor/TemperatureSensor.vue";

const props = defineProps<MimicComponentInstanceProps>();
</script>

<template>
  <TemperatureSensor v-bind="props" />
</template>
