<script setup lang="ts">
import { defineProps } from "vue";
import { RouteLocationRaw } from "vue-router";

defineProps<{ to: RouteLocationRaw; active?: boolean; disabled?: boolean }>();
</script>

<template>
  <li
    class="rounded-xl hover:bg-primary/10"
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
      class="pointer-events-none flex items-center px-3 py-2 text-primary/40"
    >
      <slot />
    </span>
  </li>
</template>
