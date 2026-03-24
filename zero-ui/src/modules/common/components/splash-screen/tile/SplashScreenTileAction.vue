<template>
  <span class="rounded-full border px-3 py-2 text-xs font-bold tracking-[0.22em] uppercase">
    <slot />
  </span>
</template>

<style scoped>
span {
  border-color: color-mix(in srgb, var(--tile-border) 55%, transparent);
  background-color: color-mix(in srgb, var(--background) 70%, transparent);
}
</style>
