<script setup lang="ts">
import { ThrsModules } from "@/modules/thrsim/lib/consts";
import { HTMLAttributes } from "vue";
import { ModeBadge, ModeBadgeSize, useModuleMode } from ".";

const props = withDefaults(
  defineProps<{
    module?: keyof ThrsModules;
    size: ModeBadgeSize;
    class?: HTMLAttributes["class"];
  }>(),
  {},
);
const modes = useModuleMode(props.module);
</script>

<template>
  <ModeBadge
    v-for="(data, index) in modes"
    :key="index"
    v-bind="data"
    :size="size"
    :class="props.class"
  />
</template>
