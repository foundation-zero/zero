<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
</script>

<template>
  <div>
    <hgroup
      :class="cn('bg-background border-border grid gap-2 rounded-md border p-3', props.class)"
    >
      <slot />
    </hgroup>
  </div>
</template>
