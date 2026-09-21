<script setup lang="ts">
import { formatNumber } from "@/modules/common/lib/utils.ts";
import { FieldRenderer, FieldRendererProps } from ".";
import { useTranslations } from "../tooltips";

const props = withDefaults(defineProps<FieldRendererProps<number>>(), { format: formatNumber.int });

const { units } = useTranslations();
const seconds = (value: number) => value % 60;
const minutes = (value: number) => Math.floor((value % 3600) / 60);
const hours = (value: number) => Math.floor(value / 3600);
</script>

<template>
  <span class="flex items-center gap-1">
    <FieldRenderer.Number
      v-bind="props"
      :unit="units('hours')"
      :transform="hours"
    />
    <FieldRenderer.Number
      v-bind="props"
      :unit="units('minutes')"
      :transform="minutes"
    />
    <FieldRenderer.Number
      v-bind="props"
      :unit="units('seconds')"
      :transform="seconds"
    />
  </span>
</template>
