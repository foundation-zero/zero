<script setup lang="ts">
import SplashOrb from "../SplashOrb.vue";

defineProps<{
  border: string;
  shadow: string;
  glow: string;
}>();
</script>

<template>
  <div
    data-slot="card"
    class="relative flex h-full min-h-80 flex-col justify-between overflow-hidden rounded-[2rem] px-6 py-6 transition-all duration-300 group-hover:-translate-y-1 group-focus-visible:-translate-y-1"
    :style="{
      '--tile-border': border,
      '--tile-shadow': shadow,
      '--tile-glow': glow,
    }"
  >
    <SplashOrb
      data-slot="orb"
      class="-right-[25%] -bottom-[35%] h-64 w-64 opacity-90 transition-all duration-350 group-hover:scale-108 group-hover:opacity-100 group-focus-visible:scale-108 group-focus-visible:opacity-100"
      :animated="false"
      center-color="var(--tile-glow)"
      fade-stop="72%"
    />

    <div
      data-slot="shine"
      class="pointer-events-none absolute inset-0 rounded-[2rem] opacity-55"
    />

    <slot />
  </div>
</template>

<style scoped>
[data-slot="card"] {
  background: linear-gradient(
    160deg,
    color-mix(in srgb, var(--background) 92%, white 8%) 0%,
    color-mix(in srgb, var(--muted) 88%, transparent) 100%
  );
  border: 1px solid color-mix(in srgb, var(--border) 72%, transparent);
  box-shadow:
    0 24px 80px color-mix(in srgb, var(--foreground) 9%, transparent),
    inset 0 1px 0 color-mix(in srgb, white 35%, transparent);
}

.group:hover [data-slot="card"],
.group:focus-visible [data-slot="card"] {
  border-color: color-mix(in srgb, var(--tile-border) 65%, var(--border));
  box-shadow:
    0 32px 90px color-mix(in srgb, var(--tile-shadow) 22%, transparent),
    inset 0 1px 0 color-mix(in srgb, white 40%, transparent);
}

[data-slot="shine"] {
  border: 1px solid color-mix(in srgb, white 24%, transparent);
  -webkit-mask-image: linear-gradient(155deg, black, transparent 45%);
  mask-image: linear-gradient(155deg, black, transparent 45%);
}
</style>
