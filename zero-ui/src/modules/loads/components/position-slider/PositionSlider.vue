<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import type { HTMLAttributes } from "vue";
const props = defineProps<{ class?: HTMLAttributes["class"] }>();
</script>

<template>
  <div
    data-slot="position-slider"
    :class="cn('bg-muted mb-4 min-h-8! w-full rounded-xs px-2', props.class)"
  >
    <slot />
  </div>
</template>
