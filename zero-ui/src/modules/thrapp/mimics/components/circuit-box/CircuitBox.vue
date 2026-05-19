<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";
import { createSizeAndViewbox } from "..";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
</script>

<template>
  <svg v-bind="createSizeAndViewbox(210, 128)">
    <foreignObject
      width="100%"
      height="100%"
    >
      <div :class="cn('flex w-49 gap-0.5', props.class)">
        <div class="bg-flows-pipe w-3 rounded-tl-md rounded-bl-md" />
        <div
          class="border-flows-pipe bg-background grow rounded-tr-md rounded-br-md border border-dashed p-2 pb-1"
        >
          <slot />
        </div>
      </div>
    </foreignObject>
  </svg>
</template>
