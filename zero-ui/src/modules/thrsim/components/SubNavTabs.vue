<script setup lang="ts">
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";

const { t } = useI18n();

const DEFAULT_PARAMS = {
  module: "dhw",
};

const menuItems = [
  {
    title: t("thrs.views.monitoring.title"),
    to: "thrsim/monitoring",
    params: DEFAULT_PARAMS,
  },
  {
    title: t("thrs.views.controls.title"),
    to: "thrsim/controls",
    params: DEFAULT_PARAMS,
  },
  {
    title: t("thrs.views.parameters.title"),
    to: "thrsim/parameters",
    params: DEFAULT_PARAMS,
  },
  {
    title: t("thrs.views.mimic.title"),
    to: "thrsim/mimic",
    params: DEFAULT_PARAMS,
  },
];

const route = useRoute();
</script>

<template>
  <Tabs :model-value="String(route.name)">
    <TabsList
      class="backdrop-blur-md"
      as="nav"
    >
      <RouterLink
        v-for="item in menuItems"
        :key="item.to"
        :to="item"
      >
        <TabsTrigger :value="item.to">
          {{ item.title }}
        </TabsTrigger>
      </RouterLink>
    </TabsList>
  </Tabs>
</template>
