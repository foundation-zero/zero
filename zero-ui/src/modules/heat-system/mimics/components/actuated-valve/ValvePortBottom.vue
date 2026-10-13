<script setup lang="ts">
import ValvePort from "./ValvePort.vue";

defineProps<{ flow: number }>();
</script>

<template>
  <ValvePort
    d="M18 18L10 30L26 30L18 18Z"
    :flow="flow"
  />
</template>
