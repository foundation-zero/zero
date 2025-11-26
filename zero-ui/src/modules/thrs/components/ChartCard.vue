<script setup lang="ts">
defineProps<{ title: string }>();
</script>

<template>
  <hgroup class="bg-background border-border grid rounded-md border">
    <header class="p-3 font-semibold capitalize">
      {{ title }}
    </header>
    <p class="h-[400px] grow p-3">
      <slot />
    </p>
  </hgroup>
</template>
