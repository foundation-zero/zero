<script setup lang="ts">
import { ThrsModules } from "@/modules/thrs/lib/consts.types";
import { Tabs, TabsList, TabsTrigger } from "@common/components/tab-links";
import { useI18n } from "vue-i18n";
import { RouterLink, useRoute } from "vue-router";
import RouterLinkWithFallback from "./RouterLinkWithFallback.vue";

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
          name: activeModule !== 'simulation' ? currentRoute.name : 'thrs/hmi/controls',
          params: { module: key },
        }"
      >
        <TabsTrigger
          :value="key"
          class="font-headers h-16 text-base font-semibold capitalize md:text-xl lg:text-2xl"
        >
          {{ key }}
        </TabsTrigger>
      </RouterLinkWithFallback>

      <RouterLink :to="{ name: 'thrs/hmi/simulation' }">
        <TabsTrigger
          value="simulation"
          class="font-headers h-16 text-base font-semibold capitalize md:text-xl lg:text-2xl"
        >
          {{ t("thrs.views.simulation.title") }}
        </TabsTrigger>
      </RouterLink>
    </TabsList>
  </Tabs>
</template>
