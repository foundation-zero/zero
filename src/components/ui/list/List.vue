<template>
  <ul>
    <slot />
  </ul>
</template>

<style lang="scss" scoped>
ul {
  @apply mt-2 grid grid-cols-1 divide-y overflow-hidden rounded-xl bg-muted/80 py-0 hover:cursor-pointer;
}
</style>
