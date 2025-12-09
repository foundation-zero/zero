<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
</script>

<template>
  <p :class="cn('h-[400px] grow', props.class)"><slot /></p>
</template>
