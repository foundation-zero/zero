<script setup lang="ts">
import { ThrsModules } from "@/modules/thrapp/lib/consts";
import { HTMLAttributes, toRef } from "vue";
import { ModeBadge, ModeBadgeSize, ModeTarget, useModuleMode } from ".";

const props = withDefaults(
  defineProps<{
    module?: keyof ThrsModules;
    /** Only show these targets of a multi-target module, e.g. `["owners"]` for PVT. */
    targets?: ModeTarget[];
    size: ModeBadgeSize;
    class?: HTMLAttributes["class"];
  }>(),
  {},
);

const modes = useModuleMode(toRef(props, "module"), toRef(props, "targets"));
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
