<script setup lang="ts">
import { onMounted, onUnmounted, toRefs } from "vue";
import {
  VariableGrid,
  VariableGridGroup,
  VariableGridHeader,
  VariableGridItem,
} from "../components/variable-grid";

import { useAlarmsStore } from "../stores/alarms";
import { useVariablesStore } from "../stores/variables";

const { visibleDashboardGroups, selectedDashboard, selectedCardType } = toRefs(useVariablesStore());
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
    <VariableGrid :type="selectedCardType">
      <VariableGridGroup
        v-for="group in visibleDashboardGroups"
        :key="group.name"
        :items="group.variables"
      >
        <VariableGridHeader>
          {{ group.name }}
        </VariableGridHeader>

        <template #item="{ variable }">
          <VariableGridItem
            :id="variable.id"
            :variable="variable"
          />
        </template>
      </VariableGridGroup>
    </VariableGrid>
  </article>
</template>
