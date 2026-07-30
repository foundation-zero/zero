<script setup lang="ts">
defineProps<{ label?: string | null }>();
</script>

<template>
  <p
    v-if="label"
    class="text-muted-foreground text-xs leading-none font-medium whitespace-nowrap"
  >
    {{ label }}
  </p>
</template>
