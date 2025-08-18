<script setup lang="ts">
import { RouteLocationRaw } from "vue-router";

defineProps<{ to: RouteLocationRaw; active?: boolean; disabled?: boolean }>();
</script>

<template>
  <li
    class="hover:bg-primary/10 rounded-md"
    :class="{
      'bg-primary/10 font-medium': active,
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
