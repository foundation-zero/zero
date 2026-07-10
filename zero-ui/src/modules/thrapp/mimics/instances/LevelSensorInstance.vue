<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import LevelSensor from "../components/level-sensor/LevelSensor.vue";
import { getMimicDataProvider } from "../providers";

const props = defineProps<MimicComponentInstanceProps>();
const { getComponentState } = getMimicDataProvider();
const state = getComponentState();
</script>

<template>
  <LevelSensor
    v-bind="props"
    :state="state"
  />
</template>
