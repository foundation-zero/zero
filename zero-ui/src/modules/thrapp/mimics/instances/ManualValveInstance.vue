<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import { ManualValveProps } from "../components/manual-valve";
import ManualValve from "../components/manual-valve/ManualValve.vue";

const props = defineProps<MimicComponentInstanceProps & ManualValveProps>();
</script>

<template>
  <ManualValve v-bind="props" />
</template>
