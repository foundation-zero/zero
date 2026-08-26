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
    title: t("thrs.views.monitoring.title"),
    name: "thrsim/monitoring",
    params: { module: currentModule.value },
  },
  {
    title: t("thrs.views.controls.title"),
    name: "thrsim/controls",
    params: { module: currentModule.value },
  },
  {
    title: t("thrs.views.parameters.title"),
    name: "thrsim/parameters",
    params: { module: currentModule.value },
  },
  {
    title: t("thrs.views.mimic.title"),
    name: "thrsim/mimic",
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
