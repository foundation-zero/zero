<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { computed } from "vue";
import { createUnbrokenRowGroups } from ".";
import { getContext, getGridSize, getGroupsWithVariables } from "../..";

const { groups, type, dynamicDashboard, variables } = getContext();

const rowGroups = computed(() => {
  const _getGroupWithVariables = getGroupsWithVariables(variables.value, dynamicDashboard.value);
  const groupWithVariables = groups.value.map(_getGroupWithVariables);

  return createUnbrokenRowGroups(groupWithVariables, getGridSize(type.value));
});
</script>

<template>
  <div :class="cn('grid gap-4')">
    <template
      v-for="gridGroup in rowGroups"
      :key="gridGroup.group.name"
    >
      <div class="bg-background/50 px-4 pt-3 pb-4">
        <slot v-bind="gridGroup" />
      </div>
    </template>
  </div>
</template>
