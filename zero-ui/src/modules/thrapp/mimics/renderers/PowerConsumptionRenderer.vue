<script setup lang="ts">
import { formatNumber, joulesToWatthours, scaleNumber } from "@/modules/common/lib/utils";
import { FieldRenderer, FieldRendererProps } from ".";
import { useTranslations } from "../tooltips";

const props = withDefaults(defineProps<FieldRendererProps<number>>(), {
  format: formatNumber.default,
});

const transform = (val: number) => scaleNumber(joulesToWatthours(val));

const { units } = useTranslations();

const unit = (val: number) => {
  if (val < 1_000) return units("watthours");
  else if (val < 1_000_000) return units("kilowatthours");
  else return units("megawatthours");
};
</script>

<template>
  <FieldRenderer.Number
    v-bind="props"
    class="gap-1"
    :unit="unit"
    :transform="transform"
  />
</template>
