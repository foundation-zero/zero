<script setup lang="ts">
import { DarkModeToggle } from "@/modules/common/components/dark-mode";
</script>

<template>
  <div class="toggle grid size-12 place-items-center rounded-xl max-[560px]:size-11">
    <DarkModeToggle />
  </div>
</template>

<style scoped>
.toggle {
  background: var(--splash-switch-bg);
  color: var(--brand);
}
</style>
