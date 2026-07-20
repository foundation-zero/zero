<script setup lang="ts">
import { formatNumber, toSignedNumber } from "@/modules/common/lib/utils.ts";
import { FieldRenderer, FieldRendererProps } from ".";
import { useTranslations } from "../tooltips";

const props = withDefaults(defineProps<FieldRendererProps<number>>(), {
  format: toSignedNumber(formatNumber.default),
});

const { units } = useTranslations();
</script>

<template>
  <FieldRenderer.Number
    v-bind="props"
    :unit="units('celsius')"
  />
</template>
