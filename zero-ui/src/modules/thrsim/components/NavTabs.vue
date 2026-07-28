<script setup lang="ts">
import { ThrsModules } from "@/modules/thrsim/lib/consts.types";
import RouterLinkWithFallback from "@common/components/RouterLinkWithFallback.vue";
import { Tabs, TabsList, TabsTrigger } from "@common/components/tab-links";
import { useI18n } from "vue-i18n";
import { RouterLink, useRoute } from "vue-router";

defineProps<{ modules: Array<keyof ThrsModules> }>();
const activeModule = defineModel<string | undefined>("activeModule", { required: true });
const currentRoute = useRoute();

const { t } = useI18n();
</script>

<template>
  <Tabs
    :model-value="activeModule"
    data-testid="hmi-nav"
  >
    <TabsList
      as="nav"
      class="py-0"
    >
      <RouterLinkWithFallback
        v-for="key in modules"
        :key="key"
        :to="{
          name: activeModule !== 'simulation' ? currentRoute.name : 'thrsim/controls',
          params: { module: key },
        }"
      >
        <TabsTrigger :value="key">
          {{ key }}
        </TabsTrigger>
      </RouterLinkWithFallback>

      <RouterLink :to="{ name: 'thrsim/simulation' }">
        <TabsTrigger value="simulation">
          {{ t("thrs.views.simulation.title") }}
        </TabsTrigger>
      </RouterLink>
    </TabsList>
  </Tabs>
</template>
