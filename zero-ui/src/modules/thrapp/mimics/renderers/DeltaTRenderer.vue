<script setup lang="ts">
import { formatUnit } from "@/modules/common/lib/utils.ts";
import { FieldRenderer, FieldRendererProps } from ".";

const props = withDefaults(defineProps<FieldRendererProps<number>>(), {
  format: formatUnit("celsius", 1, { signDisplay: "always" }),
});
</script>

<template>
  <FieldRenderer.Number v-bind="props" />
</template>
