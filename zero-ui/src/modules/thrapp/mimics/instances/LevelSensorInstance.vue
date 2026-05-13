<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import LevelSensor from "../components/level-sensor/LevelSensor.vue";

const props = defineProps<MimicComponentInstanceProps>();
</script>

<template>
  <LevelSensor v-bind="props" />
</template>
