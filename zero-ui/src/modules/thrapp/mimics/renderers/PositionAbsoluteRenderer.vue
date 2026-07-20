<script setup lang="ts">
import { formatNumber } from "@/modules/common/lib/utils";
import { FieldRenderer, FieldRendererProps } from ".";
import { useTranslations } from "../tooltips";

const props = withDefaults(defineProps<FieldRendererProps<number>>(), {
  format: (value: number) => formatNumber.default(value * 360),
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
