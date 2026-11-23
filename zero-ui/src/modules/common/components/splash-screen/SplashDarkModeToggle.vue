<script setup lang="ts">
import { DarkModeToggle } from "@/modules/common/components/dark-mode";
</script>

<template>
  <div class="toggle grid size-12 place-items-center rounded-xl max-[560px]:size-11">
    <DarkModeToggle class="text-brand hover:text-brand size-full rounded-xl" />
  </div>
</template>

<style scoped>
.toggle {
  background: var(--splash-switch-bg);
}

.toggle :deep(svg) {
  width: 24px;
  height: 24px;
}
</style>
