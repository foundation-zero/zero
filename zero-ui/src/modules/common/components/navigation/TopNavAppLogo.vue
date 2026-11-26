<script setup lang="ts">
import { HTMLAttributes } from "vue";
import { cn } from "../../lib/utils";
import { ZeroLogo } from "../zero-logo";

const props = withDefaults(
  defineProps<{
    class?: HTMLAttributes["class"];
    tag?: keyof HTMLElementTagNameMap;
    /** Classes for the app name after the logo, e.g. its colour. */
    suffixClass?: HTMLAttributes["class"];
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
    <span
      :class="cn('text-disabled-foreground text-xs font-extralight uppercase', props.suffixClass)"
    >
      <slot />
    </span>
  </component>
</template>
