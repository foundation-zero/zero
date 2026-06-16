<script setup lang="ts">
import { formatInt } from "@/modules/common/lib/utils.ts";
import { FieldRenderer, FieldRendererProps } from ".";
import { useTranslations } from "../tooltips";

const props = withDefaults(defineProps<FieldRendererProps<number>>(), {
  format: formatInt,
});

const { units } = useTranslations();
const seconds = (value: number) => formatInt(value % 60);
const minutes = (value: number) => formatInt(Math.floor((value % 3600) / 60));
const hours = (value: number) => formatInt(Math.floor(value / 3600));
</script>

<template>
  <span class="flex items-center gap-1">
    <FieldRenderer.Number
      v-bind="props"
      :unit="units('hours')"
      :format="hours"
    />
    <FieldRenderer.Number
      v-bind="props"
      :unit="units('minutes')"
      :format="minutes"
    />
    <FieldRenderer.Number
      v-bind="props"
      :unit="units('seconds')"
      :format="seconds"
    />
  </span>
</template>
