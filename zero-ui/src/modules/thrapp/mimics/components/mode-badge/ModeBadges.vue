<script setup lang="ts">
import { ThrsModules } from "@/modules/thrsim/lib/consts";
import { toRef } from "vue";
import { ModeBadge, ModeBadgeSize, useModuleMode } from ".";

const props = withDefaults(defineProps<{ module?: keyof ThrsModules; size: ModeBadgeSize }>(), {});
const modes = useModuleMode(toRef(props, "module"));
</script>

<template>
  <ModeBadge
    v-for="(data, index) in modes"
    :key="index"
    v-bind="data"
    :size="size"
  />
</template>
