<script setup lang="ts">
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/shadcn/tabs";
import { toRefs } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";
const { name } = toRefs(useRoute());
const { t } = useI18n();
</script>

<template>
  <Tabs
    data-testid="thrs-nav"
    :model-value="String(name)"
  >
    <TabsList
      class="backdrop-blur-md"
      as="nav"
    >
      <TabsTrigger
        value="thrs/dashboard"
        disabled
      >
        {{ t("labels.dashboard") }}
      </TabsTrigger>

      <RouterLink :to="{ name: 'thrs/main' }">
        <TabsTrigger value="thrs/main">
          {{ t("labels.thrs") }}
        </TabsTrigger>
      </RouterLink>

      <TabsTrigger
        value="thrs/electricity"
        disabled
      >
        {{ t("labels.electricity") }}
      </TabsTrigger>
    </TabsList>
  </Tabs>
</template>
