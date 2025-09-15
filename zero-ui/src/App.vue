<script setup lang="ts">
import { useDark, usePreferredDark } from "@vueuse/core";
import { onMounted } from "vue";
import Layout from "./layouts/Base.vue";

const isDark = useDark();

onMounted(() => {
  const prefersDark = usePreferredDark();

  isDark.value = prefersDark.value;
});
</script>

<template>
  <Layout>
    <RouterView />
  </Layout>
</template>
