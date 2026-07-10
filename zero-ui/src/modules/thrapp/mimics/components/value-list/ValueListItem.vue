<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
</script>

<template>
  <li :class="cn('flex flex-nowrap items-center justify-between text-nowrap', props.class)">
    <slot />
  </li>
</template>
