<script setup lang="ts">
import { useUIStore } from "@/stores/ui";
import { toRefs } from "vue";
const { isScrolling, breakpoints } = toRefs(useUIStore());
</script>

<template>
  <div
    class="top-nav"
    :class="{ '--scrolling': isScrolling }"
  >
    <slot />
    <div
      class="bar"
      :class="{ 'xl:container xl:px-6': !breakpoints.touch }"
    >
      <div class="left">
        <slot name="left"> </slot>
      </div>

      <slot name="center"></slot>

      <div class="right">
        <slot name="right"> </slot>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.top-nav {
  @apply fixed left-0 right-0 top-0 transition-all;
}

.bar {
  @apply flex items-center justify-between px-4 md:px-6;
}

.left {
  @apply grow transition-opacity;
}

.right {
  @apply flex grow flex-row items-end justify-end transition-opacity;
}

.top-nav.--scrolling {
  .bar {
    @apply max-md:dark:border-b max-sm:bg-background max-sm:py-1 max-sm:shadow-sm md:pt-2;
  }

  .left {
    @apply md:opacity-0;
  }

  .right {
    @apply max-sm:hidden md:opacity-0;
  }
}

.top-nav:not(.--scrolling) {
  .bar {
    @apply pt-3 md:pt-4;
  }
}
</style>
