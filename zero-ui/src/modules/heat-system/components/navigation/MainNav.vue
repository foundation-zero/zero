<script setup lang="ts">
import { Tabs, TabsList, TabsTrigger } from "@common/components/tab-links";
import { useI18n } from "vue-i18n";
import { RouterLink, useRoute } from "vue-router";

const currentRoute = useRoute();

const { t } = useI18n();
</script>

<template>
  <Tabs
    :model-value="String(currentRoute.name)"
    data-testid="heat-system-nav"
  >
    <TabsList
      as="nav"
      class="py-0"
    >
      <RouterLink :to="{ name: 'heat-system/control', params: { module: 'dhw' } }">
        <TabsTrigger value="heat-system/control">
          {{ t("heatSystem.views.control.title") }}
        </TabsTrigger>
      </RouterLink>
      <RouterLink :to="{ name: 'heat-system/mimics', params: { module: 'dhw' } }">
        <TabsTrigger value="heat-system/mimics">
          {{ t("heatSystem.views.mimics.title") }}
        </TabsTrigger>
      </RouterLink>
    </TabsList>
  </Tabs>
</template>
