<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
</script>

<template>
  <header :class="cn('bg-background grow-0 px-3 py-1 text-xl font-medium', props.class)">
    <slot />
  </header>
</template>
