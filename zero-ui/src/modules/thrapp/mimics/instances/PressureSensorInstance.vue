<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import PressureSensor from "../components/pressure-sensor/PressureSensor.vue";

const props = defineProps<MimicComponentInstanceProps>();
</script>

<template>
  <PressureSensor v-bind="props" />
</template>
