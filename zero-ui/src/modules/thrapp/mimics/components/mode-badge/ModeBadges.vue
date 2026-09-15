<script setup lang="ts">
import { ThrsModules } from "@/modules/thrsim/lib/consts";
import { computed } from "vue";
import { compute_module_mode, ModeBadge, ModeBadgeSize } from ".";

const props = withDefaults(defineProps<{ module?: keyof ThrsModules; size: ModeBadgeSize }>(), {});

const modes = computed(() => {
  return compute_module_mode(props.module);
});
</script>

<template>
  <ModeBadge
    v-for="(data, index) in modes"
    :key="index"
    v-bind="data"
    :size="size"
  />
</template>
