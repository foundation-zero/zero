<script setup lang="ts">
import NavTabs from "@/modules/thrs/components/NavTabs.vue";
import { useI18n } from "vue-i18n";

import SimulationActions from "@/modules/thrs/components/SimulationActions.vue";

import TopNav from "@/modules/common/components/navigation/TopNav.vue";
import TopNavAppLogo from "@/modules/common/components/navigation/TopNavAppLogo.vue";
import TopNavToolbar from "@/modules/common/components/navigation/TopNavToolbar.vue";
import { client } from "@/modules/thrs/graphql/client";
import { ThrsModules } from "@/modules/thrs/lib/consts.types";
import { useThrsHistory } from "@/modules/thrs/stores/history";
import { RiSeparator } from "@remixicon/vue";
import { provideClient } from "@urql/vue";
import { computed, provide, toRefs } from "vue";
import { useRoute } from "vue-router";
import ClearChartHistory from "../components/ClearChartHistory.vue";
import ControlActions from "../components/ControlActions.vue";
import SimulationTabs from "../components/SimulationTabs.vue";
import SubNavTabs from "../components/SubNavTabs.vue";

// Provide the URL client to inner scope. Pinia stores have their own scope, so they need to manually provide the correct context.
provideClient(client);

const { t } = useI18n();

const currentRoute = useRoute();
const modules: Array<keyof ThrsModules> = ["thrusters", "pvt", "pcm", "consumers", "boilers"];
const currentModuleKey = computed(() => {
  if (currentRoute.params.module) return currentRoute.params.module as string;
  if (currentRoute.name === "thrs/hmi/overview") return "overview";
  return "simulation";
});
const isSimulationRoute = computed(() => currentRoute.name === "thrs/hmi/simulation");
const isModuleRoute = computed(() => Boolean(currentRoute.params.module));

const { data } = toRefs(useThrsHistory());
const isSimulationEnvironment = computed(
  () => (data.value?.environment ?? "simulation") === "simulation",
);

provide("currentModule", currentModuleKey);
</script>

<template>
  <main class="h-svh pt-[12em] pb-8 md:pt-[14em]">
    <Suspense>
      <article class="px-4 pb-8 md:px-6">
        <slot />
      </article>
    </Suspense>
  </main>
  <TopNav class="z-1">
    <TopNavToolbar>
      <template #left-content>
        <TopNavAppLogo>
          {{ t("apps.thrs") }}
        </TopNavAppLogo>

        <NavTabs
          :active-module="currentModuleKey"
          class="md:ml-4"
          :modules="modules"
        />
      </template>

      <template #right-content>
        <ClearChartHistory />
        <template v-if="isSimulationEnvironment">
          <RiSeparator class="text-disabled-foreground" />
          <SimulationActions class="max-md:hidden" />
        </template>
      </template>
    </TopNavToolbar>
    <TopNavToolbar
      v-if="isModuleRoute || isSimulationRoute"
      class="py-1 transition-all duration-300 md:py-2"
    >
      <template #left>
        <SubNavTabs v-if="isModuleRoute" />
        <SimulationTabs v-else-if="isSimulationRoute" />
      </template>
      <template
        v-if="isModuleRoute"
        #right
      >
        <ControlActions :module="currentModuleKey" />
      </template>
    </TopNavToolbar>
  </TopNav>
</template>
