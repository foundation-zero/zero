<script setup lang="ts">
import { Tabs, TabsList, TabsTrigger } from "@common/components/tab-links";
import { usePowerTagsStore } from "../../stores/power-tags";

const store = usePowerTagsStore();
</script>

<template>
  <Tabs
    :model-value="store.activePanel"
    data-testid="power-tags-tabs"
    @update:model-value="store.activePanel = String($event)"
  >
    <TabsList
      as="nav"
      class="py-0"
      data-testid="power-tags-tabs-list"
    >
      <TabsTrigger
        v-for="panel in store.sortedPanels"
        :key="panel.id"
        :value="panel.id"
        :data-testid="`power-tags-tab-${panel.id}`"
      >
        {{ panel.id }}
      </TabsTrigger>
    </TabsList>
  </Tabs>
</template>
