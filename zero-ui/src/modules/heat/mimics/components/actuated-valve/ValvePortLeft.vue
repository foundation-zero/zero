<script setup lang="ts">
import ValvePort from "./ValvePort.vue";

defineProps<{ flow: number }>();
</script>

<template>
  <ValvePort
    d="M18 18L6 26L6 10L18 18Z"
    :flow="flow"
  />
</template>
