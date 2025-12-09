<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
</script>

<template>
  <div
    data-slot="target-box-line"
    :class="cn('bg-constructive h-[0.6875rem] w-[0.03125rem]', props.class)"
  />
</template>
