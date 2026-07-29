<script setup lang="ts">
defineProps<{ label?: string | null }>();
</script>

<template>
  <p
    v-if="label"
    class="text-muted-foreground whitespace-nowrap text-xs font-medium leading-none"
  >
    {{ label }}
  </p>
</template>
