<script setup lang="ts">
import { BREAKPOINTS } from "@/modules/common/stores/ui";
import { computed, toRefs } from "vue";
import { provideContext } from ".";
import { VariableGroup } from "../../lib/consts.dashboards";
import { CardType, MaybeVariable, SailPositionGroup } from "../../types";
import { ColumnLayout } from "./strategies/columns";
import { RowLayout } from "./strategies/rows";

const props = defineProps<{
  groups: VariableGroup[];
  type: CardType;
  rowLayout: RowLayout;
  columnLayout: ColumnLayout | RowLayout;
  dynamicDashboard: boolean;
  variables: MaybeVariable[];
  positionGroups: SailPositionGroup[];
}>();

const isLargeEnoughForColumns = computed(() => BREAKPOINTS.greaterOrEqual("xl").value);

provideContext(toRefs(props));
</script>

<template>
  <component
    :is="columnLayout"
    v-if="isLargeEnoughForColumns"
  >
    <template #default="gridProps">
      <slot v-bind="gridProps" />
    </template>
  </component>
  <component
    :is="rowLayout"
    v-else
  >
    <template #default="gridProps">
      <slot v-bind="gridProps" />
    </template>
  </component>
</template>
