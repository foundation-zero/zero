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
    data-testid="thrapp-nav"
  >
    <TabsList
      as="nav"
      class="py-0"
    >
      <RouterLink :to="{ name: 'thrs/control', params: { module: 'dhw' } }">
        <TabsTrigger value="thrs/control">
          {{ t("thrapp.views.control.title") }}
        </TabsTrigger>
      </RouterLink>
      <RouterLink :to="{ name: 'thrs/mimics', params: { module: 'dhw' } }">
        <TabsTrigger value="thrs/mimics">
          {{ t("thrapp.views.mimics.title") }}
        </TabsTrigger>
      </RouterLink>
    </TabsList>
  </Tabs>
</template>
