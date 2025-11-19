<script setup lang="ts">
import TopNav from "../components/TopNav.vue";
</script>

<template>
  <main class="h-svh pt-[10em] pb-8 max-2xl:px-6 max-lg:px-4 2xl:container 2xl:mx-auto">
    <Suspense>
      <slot />
    </Suspense>
  </main>
  <TopNav />
</template>
