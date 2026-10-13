<script setup lang="ts">
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";

const { t } = useI18n();

const route = useRoute();
const currentModule = computed(() => (route.params.module as string) || "dhw");

const menuItems = computed(() => [
  {
    title: t("heatSystemSimulation.views.monitoring.title"),
    name: "heat-system-simulation/monitoring",
    params: { module: currentModule.value },
  },
  {
    title: t("heatSystemSimulation.views.controls.title"),
    name: "heat-system-simulation/controls",
    params: { module: currentModule.value },
  },
  {
    title: t("heatSystemSimulation.views.parameters.title"),
    name: "heat-system-simulation/parameters",
    params: { module: currentModule.value },
  },
  {
    title: t("heatSystemSimulation.views.mimic.title"),
    name: "heat-system-simulation/mimic",
    params: { module: currentModule.value },
  },
]);
</script>

<template>
  <Tabs :model-value="String(route.name)">
    <TabsList
      class="backdrop-blur-md"
      as="nav"
    >
      <RouterLink
        v-for="item in menuItems"
        :key="item.name"
        :to="{ name: item.name, params: item.params }"
      >
        <TabsTrigger :value="item.name">
          {{ item.title }}
        </TabsTrigger>
      </RouterLink>
    </TabsList>
  </Tabs>
</template>
