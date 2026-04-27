<script setup lang="ts">
import { ThrsModules } from "@/modules/thrs/lib/consts.types";
import { useThrsHistory } from "@/modules/thrs/stores/history";
import RouterLinkWithFallback from "@common/components/RouterLinkWithFallback.vue";
import { Tabs, TabsList, TabsTrigger } from "@common/components/tab-links";
import { toRefs } from "vue";
import { useI18n } from "vue-i18n";
import { RouterLink, useRoute } from "vue-router";

defineProps<{ modules: Array<keyof ThrsModules> }>();
const activeModule = defineModel<string | undefined>("activeModule", { required: true });
const currentRoute = useRoute();
const { data } = toRefs(useThrsHistory());

const { t } = useI18n();

const isModuleDisabled = (module: keyof ThrsModules): boolean =>
  data.value?.environment !== "simulation" &&
  data.value?.modules[module]?.advisoryControlEnabled === null;

const showSimulationTab = () => data.value?.environment === "simulation";
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
      <RouterLink :to="{ name: 'thrs/hmi/overview' }">
        <TabsTrigger value="overview">
          {{ t("thrs.views.overview.title") }}
        </TabsTrigger>
      </RouterLink>
      <template
        v-for="key in modules"
        :key="key"
      >
        <RouterLinkWithFallback
          v-if="!isModuleDisabled(key)"
          :to="{
            name:
              activeModule && !['simulation', 'overview'].includes(activeModule)
                ? currentRoute.name
                : 'thrs/hmi/controls',
            params: { module: key },
          }"
        >
          <TabsTrigger :value="key">
            {{ key }}
          </TabsTrigger>
        </RouterLinkWithFallback>
        <span v-else>
          <TabsTrigger
            :value="key"
            disabled
          >
            {{ key }}
          </TabsTrigger>
        </span>
      </template>

      <RouterLink
        v-if="showSimulationTab()"
        :to="{ name: 'thrs/hmi/simulation' }"
      >
        <TabsTrigger value="simulation">
          {{ t("thrs.views.simulation.title") }}
        </TabsTrigger>
      </RouterLink>
    </TabsList>
  </Tabs>
</template>
