<script setup lang="ts">
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";

const { t } = useI18n();

// Menu items.
const menuItems = [
  {
    title: t("thrs.views.monitoring.title"),
    to: "thrs/hmi/monitoring",
  },
  {
    title: t("thrs.views.controls.title"),
    to: "thrs/hmi/controls",
  },
  {
    title: t("thrs.views.parameters.title"),
    to: "thrs/hmi/parameters",
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
        :to="{ name: item.to }"
      >
        <TabsTrigger
          :value="item.to"
          class="text-sm md:text-base"
        >
          {{ item.title }}
        </TabsTrigger>
      </RouterLink>
    </TabsList>
  </Tabs>
</template>
