<script setup lang="ts">
import type { HTMLAttributes } from "vue";
import { RouterLinkProps } from "vue-router";

defineProps<
  { to: RouterLinkProps["to"]; disabled?: boolean } & { class?: HTMLAttributes["class"] }
>();
</script>

<template>
  <RouterLink
    v-if="!disabled"
    :to="to"
  >
    <slot />
  </RouterLink>
  <slot v-else />
</template>
