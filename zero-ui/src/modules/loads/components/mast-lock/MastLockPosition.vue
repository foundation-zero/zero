<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import type { HTMLAttributes } from "vue";
import {
  IndicatorLight,
  indicatorLightVariants,
  type IndicatorLightVariants,
} from "../indicator-light";

const props = defineProps<{
  status?: IndicatorLightVariants["variant"];
  class?: HTMLAttributes["class"];
}>();
</script>

<template>
  <div
    data-slot="mast-lock-position"
    :class="
      cn(
        'text-disabled-foreground flex flex-col items-center justify-center gap-4 self-stretch px-6 text-sm font-medium',
        indicatorLightVariants({ variant: status }),
        props.class,
      )
    "
  >
    <slot />
    <IndicatorLight :variant="status" />
  </div>
</template>

<style lang="scss" scoped>
[data-slot="mast-lock-position"] {
  &.constructive {
    color: var(--color-constructive-muted);
    text-shadow: 0 0 4px var(--color-constructive);
  }

  &.destructive {
    color: var(--color-destructive);
    text-shadow: 0 0 4px var(--color-destructive);
  }
}
</style>
