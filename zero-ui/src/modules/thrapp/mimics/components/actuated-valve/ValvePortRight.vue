<script setup lang="ts">
import ValvePort from "./ValvePort.vue";

defineProps<{ flow: number }>();
</script>

<template>
  <ValvePort
    d="M18 18L30 10L30 26L18 18Z"
    :flow="flow"
  />
</template>
