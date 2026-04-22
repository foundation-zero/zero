<script setup lang="ts">
import { NavItem } from "@/modules/common/types";
import { Tabs, TabsList, TabsTrigger } from "@common/components/tab-links";
import { toRefs } from "vue";
import { useI18n } from "vue-i18n";
import { DashboardType } from "../lib/consts.dashboards";
import { useVariablesStore } from "../stores/variables";

const { availableDashboards, selectedDashboard } = toRefs(useVariablesStore());
const { setDashboard } = useVariablesStore();
const { t } = useI18n();

const navItems: NavItem[] = [
  { title: "overview", to: DashboardType.Static },
  { title: "dynamic", to: DashboardType.Dynamic },
];
</script>

<template>
  <Tabs
    :model-value="selectedDashboard.id"
    @update:model-value="setDashboard"
  >
    <TabsList
      as="nav"
      class="py-0"
    >
      <TabsTrigger
        v-for="item in navItems"
        :key="item.to"
        :value="item.to"
      >
        {{ t(`loads.dashboards.${item.title}`) }}
      </TabsTrigger>

      <TabsTrigger
        v-for="item in availableDashboards"
        :key="item.id"
        :value="item.id"
      >
        {{ item.name }}
      </TabsTrigger>
    </TabsList>
  </Tabs>
</template>
