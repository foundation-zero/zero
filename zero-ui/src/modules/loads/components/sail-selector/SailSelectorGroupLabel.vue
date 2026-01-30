<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
</script>

<template>
  <h6 :class="cn('text-inverse-foreground text-xl font-semibold', props.class)">
    <slot />
  </h6>
</template>
