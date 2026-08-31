<script setup lang="ts">
import { formatRatio } from "@/modules/common/lib/utils.ts";
import { FieldRenderer, FieldRendererProps } from ".";

const props = withDefaults(defineProps<FieldRendererProps<number>>(), {
  format: formatRatio.default,
});
</script>

<template>
  <FieldRenderer.Number
    v-bind="props"
    dense
  />
</template>
