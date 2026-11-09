<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import type { HTMLAttributes } from "vue";
import { useI18n } from "vue-i18n";
import { LayerFilterOption } from "./layer-filter.provider";
import LayerFilterOptions from "./LayerFilterOptions.vue";

const props = defineProps<{ options: LayerFilterOption[]; class?: HTMLAttributes["class"] }>();

const { t } = useI18n();
</script>

<template>
  <div
    :class="
      cn(
        'bg-background flex w-fit min-w-56 flex-col gap-2 rounded-md border p-3 pt-4.5',
        props.class,
      )
    "
  >
    <h2 class="font-ui! border-border-subtle border-b pb-1.5 text-base leading-4! font-medium">
      {{ t("thrapp.labels.view") }}
    </h2>
    <LayerFilterOptions :options="options" />
  </div>
</template>
