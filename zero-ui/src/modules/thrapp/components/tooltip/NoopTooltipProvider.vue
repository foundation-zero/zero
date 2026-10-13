<script setup lang="ts">
import { ref } from "vue";
import { provideTooltipContext } from ".";

provideTooltipContext({
  setTooltip() {},
  findTooltipContext() {
    return undefined;
  },
  title: ref(null),
  getData() {
    return null;
  },
  disabled: true,
  clear() {},
  component: ref(null),
  data: ref(null),
  dialog: ref(null),
  setDialog() {},
  closeDialog() {},
});
</script>

<template>
  <slot />
</template>
