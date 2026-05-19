<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
</script>

<template>
  <li :class="cn('flex items-center justify-between', props.class)">
    <slot />
  </li>
</template>
