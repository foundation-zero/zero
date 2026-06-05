<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
</script>

<template>
  <hgroup :class="cn('flex flex-col', props.class)">
    <slot />
  </hgroup>
</template>
