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
    data-testid="heat-nav"
  >
    <TabsList
      as="nav"
      class="py-0"
    >
      <RouterLink :to="{ name: 'heat/control', params: { module: 'dhw' } }">
        <TabsTrigger value="heat/control">
          {{ t("heat.views.control.title") }}
        </TabsTrigger>
      </RouterLink>
      <RouterLink :to="{ name: 'heat/mimics', params: { module: 'dhw' } }">
        <TabsTrigger value="heat/mimics">
          {{ t("heat.views.mimics.title") }}
        </TabsTrigger>
      </RouterLink>
    </TabsList>
  </Tabs>
</template>
