<script setup lang="ts">
import { formatRatio } from "@/modules/common/lib/utils.ts";
import { FieldRenderer, FieldRendererProps } from ".";
import { useTranslations } from "../tooltips";

const props = withDefaults(defineProps<FieldRendererProps<number>>(), {
  format: formatRatio.default,
});

const { units } = useTranslations();
</script>

<template>
  <FieldRenderer.Number
    v-bind="props"
    :unit="units('percent')"
    dense
  />
</template>
