<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import CheckValve from "../components/check-valve/CheckValve.vue";

const props = defineProps<MimicComponentInstanceProps>();
</script>

<template>
  <CheckValve v-bind="props" />
</template>
