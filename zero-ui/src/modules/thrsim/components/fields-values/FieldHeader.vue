<script lang="ts" setup>
import { inject } from "vue";
const field = inject<string>("field")!;
</script>

<template>
  <header
    class="border-border-subtle text-muted-foreground col-span-full border-b border-dashed pb-3 text-2xl font-semibold capitalize"
  >
    {{ field }}
  </header>
</template>
