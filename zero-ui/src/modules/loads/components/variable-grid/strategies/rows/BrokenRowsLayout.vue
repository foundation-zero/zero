<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { computed } from "vue";
import { createBrokenRowGroups } from ".";
import { getContext, getGroupsWithVariables, toGridSize } from "../..";

const { groups, type, dynamicDashboard, variables } = getContext();

const getBrokenRowGroups = () => {
  const _getGroupWithVariables = getGroupsWithVariables(variables.value, dynamicDashboard.value);
  const groupWithVariables = groups.value.map(_getGroupWithVariables);

  return createBrokenRowGroups(groupWithVariables, type.value);
};

const rowGroups = computed(() => getBrokenRowGroups());
</script>

<template>
  <div :class="cn('grid gap-3 lg:gap-4', toGridSize(type))">
    <template v-for="gridGroup in rowGroups">
      <slot v-bind="gridGroup" />
    </template>
  </div>
</template>
