<script setup lang="ts">
import { formatUnit } from "@/modules/common/lib/utils";
import { FieldRenderer, FieldRendererProps } from ".";

const props = withDefaults(defineProps<FieldRendererProps<number>>(), {
  format: formatUnit("liter"),
});
</script>

<template>
  <FieldRenderer.Number v-bind="props" />
</template>
