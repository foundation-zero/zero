<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";
import { GridGroup } from ".";

const props = defineProps<{ group: GridGroup; class?: HTMLAttributes["class"] }>();
</script>

<template>
  <div
    v-if="group.size > 0"
    :class="cn('grid gap-3', group.gridCols, group.gridSpan, props.class)"
  >
    <slot />
  </div>
</template>
