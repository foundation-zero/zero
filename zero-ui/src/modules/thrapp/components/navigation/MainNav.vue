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
      <RouterLink :to="{ name: 'thrapp/mimics' }">
        <TabsTrigger value="thrapp/mimics">
          {{ t("thrapp.views.mimics.title") }}
        </TabsTrigger>
      </RouterLink>
    </TabsList>
  </Tabs>
</template>
