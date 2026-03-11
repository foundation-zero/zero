<script setup lang="ts">
import { useUIStore } from "./modules/common/stores/ui";

useUIStore();
</script>

<template>
  <component :is="$route.meta.layout">
    <RouterView />
  </component>
</template>
