<script setup lang="ts">
import { HTMLAttributes } from "vue";
import { cn } from "../../lib/utils";
import { ZeroLogo } from "../zero-logo";

const props = withDefaults(
  defineProps<{
    class?: HTMLAttributes["class"];
    tag?: keyof HTMLElementTagNameMap;
  }>(),
  {
    tag: "span",
  },
);
</script>

<template>
  <component
    :is="tag"
    :class="cn('flex items-center gap-1 text-nowrap max-sm:hidden', props.class)"
  >
    <ZeroLogo />
    <span class="text-disabled-foreground text-xs font-extralight uppercase">
      <slot />
    </span>
  </component>
</template>
