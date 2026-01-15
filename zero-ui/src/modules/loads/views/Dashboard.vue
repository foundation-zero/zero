<script setup lang="ts">
import { onMounted, onUnmounted } from "vue";
import {
  VariableGrid,
  VariableGridGroup,
  VariableGridHeader,
  VariableGridItem,
} from "../components/variable-grid";

import { useVariablesStore } from "../stores/variables";

const { startPolling, stopPolling } = useVariablesStore();
const { selectedDashboard } = useVariablesStore();

onMounted(startPolling);
onUnmounted(stopPolling);
</script>

<template>
  <article class="pb-4">
    <VariableGrid type="graphical">
      <VariableGridGroup
        v-for="group in selectedDashboard.groups"
        :key="group.name"
        :items="group.variables"
      >
        <VariableGridHeader>
          {{ group.name }}
        </VariableGridHeader>
        <VariableGridItem
          v-for="variableId in group.variables"
          :id="variableId"
          :key="variableId"
        />
      </VariableGridGroup>
    </VariableGrid>
  </article>
</template>
