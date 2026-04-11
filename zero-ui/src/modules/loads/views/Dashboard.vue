<script setup lang="ts">
import { onMounted, onUnmounted, toRefs } from "vue";
import {
  VariableGrid,
  VariableGridGroup,
  VariableGridHeader,
  VariableGridHeaderLabel,
  VariableGridHeaderTitle,
  VariableGridItem,
} from "../components/variable-grid";

import { useAlarmsStore } from "../stores/alarms";
import { useVariablesStore } from "../stores/variables";

const {
  visibleDashboardGroups,
  selectedCardType,
  variables,
  selectedDashboard,
  isDynamicDashboard,
  positionGroups,
} = toRefs(useVariablesStore());
const { startPolling: startPollingVariables, stopPolling: stopPollingVariables } =
  useVariablesStore();
const { startPolling: startPollingAlarms, stopPolling: stopPollingAlarms } = useAlarmsStore();

onMounted(startPollingVariables);
onMounted(startPollingAlarms);
onUnmounted(stopPollingVariables);
onUnmounted(stopPollingAlarms);
</script>

<template>
  <article class="flex flex-col gap-6 pb-4">
    <VariableGrid
      :groups="visibleDashboardGroups"
      :type="selectedCardType"
      :row-layout="selectedDashboard?.rowLayout"
      :column-layout="selectedDashboard?.columnLayout"
      :dynamic-dashboard="isDynamicDashboard"
      :variables="variables"
      :position-groups="positionGroups"
    >
      <template #default="{ group, size, variables: groupVariables, hasBooleans }">
        <VariableGridGroup
          v-if="size > 0"
          :class="[`grid-cols-${hasBooleans ? size * 3 : size}`, `col-span-${size}`]"
        >
          <VariableGridHeader>
            <VariableGridHeaderTitle>{{ group.name }}</VariableGridHeaderTitle>
            <template #right>
              <VariableGridHeaderLabel v-if="groupVariables.length < group.variables.length">
                {{
                  $t("loads.components.grid.sensorsSub", {
                    count: groupVariables.length,
                    total: group.variables.length,
                  })
                }}
              </VariableGridHeaderLabel>
              <VariableGridHeaderLabel v-else>
                {{ $t("loads.components.grid.sensors", { count: groupVariables.length }) }}
              </VariableGridHeaderLabel>
            </template>
          </VariableGridHeader>

          <VariableGridItem
            v-for="variable in groupVariables"
            :id="variable.id"
            :key="variable.id"
            :variable="variable"
          />
        </VariableGridGroup>
      </template>
    </VariableGrid>
  </article>
</template>
