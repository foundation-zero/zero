<script setup lang="ts">
import SplashGlassPill from "../SplashGlassPill.vue";
</script>

<template>
  <SplashGlassPill class="px-4 py-2">
    <span class="text-muted-foreground text-xs font-semibold tracking-[0.45em] uppercase">
      <slot />
    </span>
  </SplashGlassPill>
</template>
