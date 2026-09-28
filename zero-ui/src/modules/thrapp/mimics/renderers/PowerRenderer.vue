<script setup lang="ts">
import { formatNumber, scaleNumber } from "@/modules/common/lib/utils";
import { FieldRenderer, FieldRendererProps } from ".";
import { useTranslations } from "../tooltips";

const props = withDefaults(defineProps<FieldRendererProps<number>>(), {
  format: formatNumber.default,
});

const { units } = useTranslations();

const unit = (absRawValue: number) => {
  if (absRawValue < 1_000) return units("watt");
  else if (absRawValue < 1_000_000) return units("kilowatt");
  else return units("megawatt");
};
</script>

<template>
  <FieldRenderer.Number
    v-bind="props"
    class="gap-1"
    :unit="unit"
    :transform="scaleNumber"
  />
</template>
