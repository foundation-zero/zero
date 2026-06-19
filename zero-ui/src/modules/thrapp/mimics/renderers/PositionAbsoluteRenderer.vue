<script setup lang="ts">
import { formatInt } from "@/modules/common/lib/utils.ts";
import { FieldRenderer, FieldRendererProps } from ".";
import { useTranslations } from "../tooltips";

const props = withDefaults(defineProps<FieldRendererProps<number>>(), {
  format: (value: number) => formatInt(value * 360),
});

const { units } = useTranslations();
</script>

<template>
  <FieldRenderer.Number
    v-bind="props"
    :unit="units('degrees')"
    dense
  >
  </FieldRenderer.Number>
</template>
