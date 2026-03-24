<script setup lang="ts">
import SplashOrb from "../SplashOrb.vue";
import SplashScreenGridPattern from "./SplashScreenGridPattern.vue";
</script>

<template>
  <div class="pointer-events-none absolute inset-0">
    <SplashOrb
      class="top-[5%] left-[-8%] h-[min(38rem,62vw)] w-[min(38rem,62vw)] opacity-75 blur-[30px]"
      color="var(--brand-dull)"
      mix="42%"
      fade-stop="68%"
      animation-duration="12s"
    />

    <SplashOrb
      class="top-[-15%] right-[-12%] h-[min(35rem,55vw)] w-[min(35rem,55vw)] opacity-60 blur-[35px]"
      color="var(--warning)"
      mix="28%"
      fade-stop="70%"
      animation-duration="14s"
      animation-delay="-2s"
    />

    <SplashScreenGridPattern />
  </div>
</template>
