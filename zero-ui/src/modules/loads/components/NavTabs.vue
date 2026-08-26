<script setup lang="ts">
import { NavItem } from "@/modules/common/types";
import { Tabs, TabsList, TabsTrigger } from "@common/components/tab-links";
import { computed, toRefs } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";
import { DashboardId, DashboardType } from "../lib/consts.dashboards";
import { useVariablesStore } from "../stores/variables";

const { availableDashboards, selectedDashboard } = toRefs(useVariablesStore());
const { setDashboard } = useVariablesStore();
const { t } = useI18n();
const route = useRoute();
const router = useRouter();

const FIBER_OPTICS_VALUE = "fiber-optics";

const navItems: NavItem[] = [
  { title: "overview", to: DashboardType.Static },
  { title: "dynamic", to: DashboardType.Dynamic },
  { title: "fiberOptics", to: FIBER_OPTICS_VALUE },
];

const isFiberOpticsRoute = (name: unknown): boolean => name === "loads/fiber-optics";

const currentTab = computed((): string =>
  isFiberOpticsRoute(route.name) ? FIBER_OPTICS_VALUE : selectedDashboard.value.id,
);

const handleTabChange = (value: string): void => {
  if (value === FIBER_OPTICS_VALUE) {
    router.push({ name: "loads/fiber-optics" });
    return;
  } else {
    if (isFiberOpticsRoute(route.name)) {
      router.push({ name: "loads/dashboard" });
    }
    setDashboard(value as unknown as DashboardId);
  }
};
</script>

<template>
  <Tabs
    :model-value="currentTab"
    @update:model-value="handleTabChange"
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
