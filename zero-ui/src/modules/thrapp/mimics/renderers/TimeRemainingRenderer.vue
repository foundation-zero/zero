<script setup lang="ts">
import { formatUnit } from "@/modules/common/lib/utils.ts";
import { FieldRenderer, FieldRendererProps } from ".";

const props = defineProps<FieldRendererProps<number>>();

const toSeconds = formatUnit("second", 0, {}, (value: number) => value % 60);
const toMinutes = formatUnit("minute", 0, {}, (value: number) => Math.floor((value % 3600) / 60));
const toHours = formatUnit("hour", 0, {}, (value: number) => Math.floor(value / 3600));
</script>

<template>
  <span class="flex items-center gap-1">
    <FieldRenderer.Number
      v-bind="props"
      :format="toHours"
    />
    <FieldRenderer.Number
      v-bind="props"
      :format="toMinutes"
    />
    <FieldRenderer.Number
      v-bind="props"
      :format="toSeconds"
    />
  </span>
</template>
