<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
</script>

<template>
  <header :class="cn('mb-3 text-lg font-bold capitalize', props.class)">
    <slot />
  </header>
</template>
