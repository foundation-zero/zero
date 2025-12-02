<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { reactiveOmit } from "@vueuse/core";
import type { PrimitiveProps } from "reka-ui";
import type { HTMLAttributes } from "vue";
import { indicatorLightVariants, type IndicatorLightVariants } from ".";

const props = defineProps<
  PrimitiveProps & {
    variant?: IndicatorLightVariants["variant"];
    class?: HTMLAttributes["class"];
  }
>();

const delegatedProps = reactiveOmit(props, "class");
</script>

<template>
  <div
    data-slot="indicator-light"
    class="bg-muted size-7 rounded-full p-1"
    v-bind="delegatedProps"
  >
    <div
      data-slot="glass"
      :class="cn(indicatorLightVariants({ variant }), props.class)"
      class="size-full rounded-full"
    ></div>
  </div>
</template>

<style lang="scss" scoped>
[data-slot="glass"] {
  --color-highlight: var(--color-muted);

  background:
    radial-gradient(
      26.76% 16.85% at 37.5% 28.57%,
      rgba(255, 255, 255, 0.3) 0%,
      rgba(255, 255, 255, 0) 68.75%
    ),
    var(--color-highlight);

  &.default {
    box-shadow: 0 0 8px 0 rgba(0, 0, 0, 0.5) inset;
  }

  &.constructive {
    --color-highlight: var(--color-constructive-muted);
    box-shadow: 0 0 8px 0 var(--color-attention);
  }

  &.destructive {
    --color-highlight: var(--color-destructive);
    box-shadow: 0 0 8px 0 var(--color-destructive);
  }
}
</style>
