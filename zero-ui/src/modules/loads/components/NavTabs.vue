<script setup lang="ts">
import { Tabs, TabsList, TabsTrigger } from "@common/components/tab-links";
import { toRefs } from "vue";
import { useI18n } from "vue-i18n";
import { SailId } from "../lib/consts.sails";
import { useVariablesStore } from "../stores/variables";

const { availableDashboards, selectedDashboard } = toRefs(useVariablesStore());
const { t } = useI18n();
</script>

<template>
  <Tabs :model-value="selectedDashboard.sail">
    <TabsList
      as="nav"
      class="py-0"
    >
      <TabsTrigger
        :value="SailId.None"
        class="h-16 text-base font-medium"
      >
        {{ t("loads.dashboards.overview") }}
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
