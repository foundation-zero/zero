<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{ class?: HTMLAttributes["class"]; dense?: boolean }>();
</script>

<template>
  <ul :class="cn('grid gap-0.5', { 'gap-0 leading-[1.3]': dense }, props.class)">
    <slot />
  </ul>
</template>
