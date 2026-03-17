<script setup lang="ts">
import { computed, onMounted, onUnmounted, toRefs } from "vue";
import {
  createGridGroups,
  VariableGrid,
  VariableGridGroup,
  VariableGridHeader,
  VariableGridHeaderLabel,
  VariableGridHeaderTitle,
  VariableGridItem,
} from "../components/variable-grid";

import { useAlarmsStore } from "../stores/alarms";
import { useVariablesStore } from "../stores/variables";

const { visibleDashboardGroups, selectedCardType, variables, isDynamicDashboard } =
  toRefs(useVariablesStore());
const { startPolling: startPollingVariables, stopPolling: stopPollingVariables } =
  useVariablesStore();
const { startPolling: startPollingAlarms, stopPolling: stopPollingAlarms } = useAlarmsStore();

const gridGroups = computed(() =>
  createGridGroups(
    visibleDashboardGroups.value,
    selectedCardType.value,
    isDynamicDashboard.value,
    variables.value,
  ),
);

onMounted(startPollingVariables);
onMounted(startPollingAlarms);
onUnmounted(stopPollingVariables);
onUnmounted(stopPollingAlarms);
</script>

<template>
  <article class="flex flex-col gap-6 pb-4">
    <VariableGrid :type="selectedCardType">
      <VariableGridGroup
        v-for="(group, index) in gridGroups"
        :key="`${group.name}-${index}`"
        :group="group"
      >
        <VariableGridHeader>
          <VariableGridHeaderTitle>{{ group.name }}</VariableGridHeaderTitle>
          <template #right>
            <VariableGridHeaderLabel v-if="group.variables.length < group.totalAmount">
              {{
                $t("loads.components.grid.sensorsSub", {
                  count: group.variables.length,
                  total: group.totalAmount,
                })
              }}
            </VariableGridHeaderLabel>
            <VariableGridHeaderLabel v-else>
              {{ $t("loads.components.grid.sensors", { count: group.totalAmount }) }}
            </VariableGridHeaderLabel>
          </template>
        </VariableGridHeader>

        <VariableGridItem
          v-for="variable in group.variables"
          :id="variable.id"
          :key="variable.id"
          :variable="variable"
        />
      </VariableGridGroup>
    </VariableGrid>
  </article>
</template>
