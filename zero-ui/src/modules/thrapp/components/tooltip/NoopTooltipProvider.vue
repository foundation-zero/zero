<script setup lang="ts">
import { ref } from "vue";
import { provideTooltipContext } from ".";

provideTooltipContext({
  setTooltip() {},
  findTooltipContext() {
    return undefined;
  },
  getData() {
    return null;
  },
  disabled: true,
  clear() {},
  component: ref(null),
  data: ref(null),
});
</script>

<template>
  <slot />
</template>
