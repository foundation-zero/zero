<template>
  <div class="rounded-full border backdrop-blur-md">
    <slot />
  </div>
</template>

<style scoped>
div {
  border-color: color-mix(in srgb, var(--border-subtle) 80%, transparent);
  background-color: color-mix(in srgb, var(--background) 70%, transparent);
}
</style>
