<template>
  <ul>
    <slot />
  </ul>
</template>

<style lang="scss" scoped>
ul {
  @apply mt-2 py-0
    grid grid-cols-1 divide-y
    bg-muted rounded-xl overflow-hidden 
    hover:cursor-pointer;
}
</style>
