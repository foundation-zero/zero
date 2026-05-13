<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
</script>

<template>
  <svg
    width="100"
    height="60"
  >
    <!-- Offset on y needed because of hgroup positioning within the foreignObject -->
    <foreignObject
      width="100%"
      height="100%"
      y="-7.5"
    >
      <hgroup
        xmlns="http://www.w3.org/1999/xhtml"
        :class="cn('bg-background inline-flex flex-col rounded-[0.125rem] px-1', props.class)"
      >
        <header class="text-muted-foreground text-3xs">
          <slot />
        </header>
        <p
          v-if="$slots['value']"
          class="text-foreground text-sm font-medium"
        >
          <slot name="value" />
        </p>
      </hgroup>
    </foreignObject>
  </svg>
</template>
