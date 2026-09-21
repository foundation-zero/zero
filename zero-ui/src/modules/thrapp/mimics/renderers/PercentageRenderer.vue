<script setup lang="ts">
import { formatPercentage, ratioToPercentage } from "@/modules/common/lib/utils.ts";
import { FieldRenderer, FieldRendererProps } from ".";

const props = withDefaults(defineProps<FieldRendererProps<number>>(), {
  format: formatPercentage.default,
});
</script>

<template>
  <FieldRenderer.Number
    v-bind="props"
    :transform="ratioToPercentage"
    dense
  />
</template>
