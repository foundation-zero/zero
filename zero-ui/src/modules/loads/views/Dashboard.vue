<script setup lang="ts">
import {
  VariableGrid,
  VariableGridGroup,
  VariableGridHeader,
  VariableGridItem,
} from "../components/variable-grid";

import { OVERVIEW } from "../lib/consts.dashboards";
</script>

<template>
  <article class="pb-4">
    <VariableGrid type="graphical">
      <VariableGridGroup
        v-for="group in OVERVIEW.groups"
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
