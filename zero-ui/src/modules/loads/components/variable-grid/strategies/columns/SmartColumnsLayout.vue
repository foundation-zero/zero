<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { computed } from "vue";
import { createColumnPartitions, createSmartColumnGroups } from ".";
import { getContext, getGridSize, getGroupsWithVariables, toGridSize } from "../..";

const { groups, type, dynamicDashboard, variables, positionGroups } = getContext();

const columnGroups = computed(() => {
  const _getGroupWithVariables = getGroupsWithVariables(variables.value, dynamicDashboard.value);
  const groupWithVariables = groups.value.map(_getGroupWithVariables);
  const input = createColumnPartitions(groupWithVariables, positionGroups.value);

  return createSmartColumnGroups(input, getGridSize(type.value));
});
</script>

<template>
  <div :class="cn('grid gap-4', toGridSize(type))">
    <div
      v-for="(column, columnIndex) in columnGroups"
      :key="columnIndex"
      :class="[
        'flex flex-col gap-4',
        `col-span-${column.size}`,
        { 'bg-background/50': column.groups.length === 0 },
      ]"
    >
      <template
        v-for="group in column.groups"
        :key="group.group.name"
      >
        <div
          v-if="group"
          class="bg-background/50 px-4 pt-3 pb-4"
        >
          <slot v-bind="group" />
        </div>
      </template>
    </div>
  </div>
</template>
