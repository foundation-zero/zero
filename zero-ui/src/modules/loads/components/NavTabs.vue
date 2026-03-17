<script setup lang="ts">
import { Tabs, TabsList, TabsTrigger } from "@common/components/tab-links";
import { toRefs } from "vue";
import { useI18n } from "vue-i18n";
import { DashboardType } from "../lib/consts.dashboards";
import { useVariablesStore } from "../stores/variables";

const { availableDashboards, selectedDashboard } = toRefs(useVariablesStore());
const { setDashboard } = useVariablesStore();
const { t } = useI18n();
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
        :value="DashboardType.Static"
        class="h-16 text-base font-medium"
      >
        {{ t("loads.dashboards.overview") }}
      </TabsTrigger>
      <TabsTrigger
        :value="DashboardType.Dynamic"
        class="h-16 text-base font-medium"
      >
        {{ t("loads.dashboards.dynamic") }}
      </TabsTrigger>
      <TabsTrigger
        v-for="item in availableDashboards"
        :key="item.id"
        :value="item.id"
        class="h-16 text-base font-medium"
      >
        {{ item.name }}
      </TabsTrigger>
    </TabsList>
  </Tabs>
</template>
