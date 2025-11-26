<script setup lang="ts">
import { RouteLocationRaw } from "vue-router";

defineProps<{ to: RouteLocationRaw; active?: boolean; disabled?: boolean }>();
</script>

<template>
  <li
    class="hover:bg-background rounded-md font-light transition-all duration-250"
    :class="{
      'text-brand font-medium': active,
      'text-muted-foreground': !active,
    }"
  >
    <RouterLink
      v-if="!disabled"
      :to="to"
      class="flex items-center px-3 py-2"
    >
      <slot />
    </RouterLink>
    <span
      v-else
      class="text-primary/40 pointer-events-none flex items-center px-3 py-2"
    >
      <slot />
    </span>
  </li>
</template>
