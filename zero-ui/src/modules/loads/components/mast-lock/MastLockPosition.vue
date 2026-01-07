<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { computed, type HTMLAttributes } from "vue";
import { MastLockState } from "../../types";
import { IndicatorLight } from "../indicator-light";

const props = defineProps<{
  state?: MastLockState;
  class?: HTMLAttributes["class"];
}>();

const variant = computed(() => {
  if (props.state === "error") return "destructive";
  if (props.state === true) return "constructive";
  return "neutral";
});
</script>

<template>
  <div
    data-slot="mast-lock-position"
    :class="
      cn(
        'text-disabled-foreground flex flex-col items-center justify-center gap-3 rounded-xs pb-3 text-sm font-medium',
        variant,
        props.class,
      )
    "
  >
    <slot />
    <IndicatorLight :variant="variant" />
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

    background:
      linear-gradient(
        180deg,
        oklch(from var(--color-destructive) l c h / 0),
        oklch(from var(--color-destructive) l c h / 0.1) 100%
      ),
      var(--color-background);
  }
}
</style>
