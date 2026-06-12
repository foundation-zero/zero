<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { TooltipContent } from ".";

const tUnits = tScoped("units");
const tSources = tScoped("thrapp.tooltips.sources");
const tLabels = tScoped("thrapp.tooltips.labels");
const tItems = tScoped("thrapp.tooltips.items");
withDefaults(defineProps<{ tooltip?: TooltipContent; allowManualControl?: boolean }>(), {
  allowManualControl: false,
});
</script>

<template>
  <article class="grid gap-5">
    <slot v-bind="{ units: tUnits, labels: tLabels, sources: tSources, items: tItems }" />
  </article>
</template>
