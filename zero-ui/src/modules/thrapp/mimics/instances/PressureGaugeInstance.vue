<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import PressureGauge from "../components/pressure-gauge/PressureGauge.vue";

const props = defineProps<MimicComponentInstanceProps>();
</script>

<template>
  <PressureGauge v-bind="props" />
</template>
