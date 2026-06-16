<script setup lang="ts">
import { formatInt } from "@/modules/common/lib/utils";
import { FieldRenderer, FieldRendererProps } from ".";
import { useTranslations } from "../tooltips";

const props = withDefaults(defineProps<FieldRendererProps<number>>(), {
  format: formatInt,
});

const { units } = useTranslations();
</script>

<template>
  <FieldRenderer.Number
    v-bind="props"
    class="gap-1"
    :unit="units('watts')"
  />
</template>
