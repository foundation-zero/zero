<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

import { createSizeAndViewbox } from "..";

const props = defineProps<{
  class?: HTMLAttributes["class"];
  width: number | string;
  height: number | string;
}>();
</script>

<template>
  <svg
    v-bind="createSizeAndViewbox(props.width, props.height)"
    class="fill-background"
  >
    <foreignObject
      width="100%"
      height="100%"
    >
      <div
        :class="cn('border-constructive bg-background h-full w-full border p-2 pb-1', props.class)"
      >
        <slot />
      </div>
    </foreignObject>
  </svg>
</template>
