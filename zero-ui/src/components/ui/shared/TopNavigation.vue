<script setup lang="ts">
import { useUIStore } from "@/stores/ui";
import { toRefs } from "vue";
const { isScrolling, breakpoints } = toRefs(useUIStore());
</script>

<template>
  <div
    class="fixed top-0 right-0 left-0 transition-all"
    :class="{ '': isScrolling }"
  >
    <slot />
    <div
      class="flex items-center justify-between px-4 md:px-6"
      :class="{
        'xl:container xl:px-6': !breakpoints.touch,
        'pt-3 md:pt-4': !isScrolling,
        'max-sm:bg-background max-sm:py-1 max-sm:shadow-sm md:pt-2 max-md:dark:border-b':
          isScrolling,
      }"
    >
      <div
        class="grow transition-opacity"
        :class="{ 'md:opacity-0': isScrolling }"
      >
        <slot name="left"> </slot>
      </div>

      <slot name="center"></slot>

      <div
        class="flex grow flex-row items-end justify-end transition-opacity"
        :class="{ 'max-sm:hidden md:opacity-0': isScrolling }"
      >
        <slot name="right"> </slot>
      </div>
    </div>
  </div>
</template>
