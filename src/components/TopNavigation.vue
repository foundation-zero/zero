<script setup lang="ts">
import { useUIStore } from "@/stores/ui";
import { toRefs } from "vue";
const { isScrolling } = toRefs(useUIStore());
</script>

<template>
  <div
    class="top-nav"
    :class="{ '--scrolling': isScrolling }"
  >
    <div class="bar">
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
  @apply fixed top-0 w-full;
}

.bar {
  @apply flex container items-center justify-between;
}

.left {
  @apply transition-opacity grow;
}

.right {
  @apply items-end flex flex-row justify-end transition-opacity grow;
}

.top-nav.--scrolling {
  .bar {
    @apply max-sm:py-1 md:pt-2 max-sm:shadow-sm max-sm:bg-background max-md:dark:border-b;
  }

  .left {
    @apply md:opacity-0;
  }

  .right {
    @apply md:opacity-0 max-sm:hidden;
  }
}

.top-nav:not(.--scrolling) {
  .bar {
    @apply pt-5;
  }
}
</style>
