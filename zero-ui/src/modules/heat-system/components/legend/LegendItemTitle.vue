<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
</script>

<template>
  <header :class="cn('text-sm sm:text-base!', props.class)">
    <slot />
  </header>
</template>
