<script setup lang="ts">
import { cn, ratioAsPercentage, toInversedPercentage } from "@common/lib/utils";
import { HTMLAttributes } from "vue";
import { getContext } from ".";

defineProps<{
  class?: HTMLAttributes["class"];
}>();

const { value } = getContext();
const percentage = ratioAsPercentage(value);
</script>

<template>
  <span :class="cn('relative', $props.class)">
    <span
      class="font-extrabold"
      data-testid="blindsPosition"
    >
      <span>{{ toInversedPercentage(percentage) }}</span>
    </span>
    <span
      class="text-r3xs text-muted-foreground absolute -right-0.5 bottom-2 translate-x-full font-extralight"
      >&percnt;</span
    >
  </span>
</template>
