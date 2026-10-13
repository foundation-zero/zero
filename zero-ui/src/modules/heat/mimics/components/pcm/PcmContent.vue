<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { inject, type HTMLAttributes } from "vue";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
const contentRightPadding = inject<string>("contentRightPadding");
</script>

<template>
  <div
    :class="cn('flex flex-col gap-1.5', props.class)"
    :style="{ 'padding-right': `${contentRightPadding}px` }"
  >
    <slot />
  </div>
</template>
