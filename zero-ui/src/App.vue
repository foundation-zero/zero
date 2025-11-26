<script setup lang="ts">
import { useDark, usePreferredDark } from "@vueuse/core";
import { onMounted } from "vue";

const isDark = useDark();

onMounted(() => {
  const prefersDark = usePreferredDark();

  isDark.value = prefersDark.value;
});
</script>

<template>
  <component :is="$route.meta.layout">
    <RouterView />
  </component>
</template>
