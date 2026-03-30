<script setup lang="ts">
import NavTabs from "@/modules/thrs/components/NavTabs.vue";
import { useI18n } from "vue-i18n";

import SimulationActions from "@/modules/thrs/components/SimulationActions.vue";

import { DarkModeToggle } from "@/modules/common/components/dark-mode";
import TopNav from "@/modules/common/components/top-nav/TopNav.vue";
import TopNavToolbar from "@/modules/common/components/top-nav/TopNavToolbar.vue";
import { client } from "@/modules/thrs/graphql/client";
import { ThrsModules } from "@/modules/thrs/lib/consts.types";
import { DividerVerticalIcon } from "@radix-icons/vue";
import { provideClient } from "@urql/vue";
import { computed, provide } from "vue";
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
const currentModuleKey = computed(() => (currentRoute.params.module as string) ?? "simulation");

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
      <template #left>
        <h4 class="pl-4 font-semibold uppercase max-md:hidden md:text-4xl">
          {{ t("thrs.title") }}
        </h4>
        <NavTabs
          :active-module="currentModuleKey"
          class="md:ml-12"
          :modules="modules"
        />
      </template>

      <template #right>
        <DarkModeToggle />
        <DividerVerticalIcon class="text-disabled-foreground" />
        <ClearChartHistory />
        <DividerVerticalIcon class="text-disabled-foreground" />
        <SimulationActions class="max-md:hidden" />
      </template>
    </TopNavToolbar>
    <TopNavToolbar class="py-2 transition-all duration-300">
      <template #left>
        <SubNavTabs v-if="currentRoute.params.module" />
        <SimulationTabs v-else />
      </template>
      <template
        v-if="currentRoute.params.module"
        #right
      >
        <ControlActions :module="currentModuleKey" />
      </template>
    </TopNavToolbar>
  </TopNav>
</template>
