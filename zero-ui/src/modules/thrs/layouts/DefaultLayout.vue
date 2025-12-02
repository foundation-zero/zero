<script setup lang="ts">
import NavTabs from "@/modules/thrs/components/NavTabs.vue";
import { useI18n } from "vue-i18n";

import SimulationActions from "@/modules/thrs/components/SimulationActions.vue";

import TopNav from "@/modules/common/components/top-nav/TopNav.vue";
import TopNavToolbar from "@/modules/common/components/top-nav/TopNavToolbar.vue";
import ControlActions from "@/modules/thrs/components/ControlActions.vue";
import { client } from "@/modules/thrs/graphql/client";
import { THRSModules } from "@/modules/thrs/lib/consts.types";
import { provideClient } from "@urql/vue";
import { computed, provide } from "vue";
import { useRoute } from "vue-router";
import SubNavTabs from "../components/SubNavTabs.vue";

// Provide the URL client to inner scope. Pinia stores have their own scope, so they need to manually provide the correct context.
provideClient(client);

const { t } = useI18n();

const currentRoute = useRoute();
const modules: Array<keyof THRSModules> = ["thrusters", "pvt", "pcm", "consumers"];
const currentModuleKey = computed(() => (currentRoute.params.module as string) || modules[0]);

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
  <TopNav class="z-100 min-h-[8rem]">
    <TopNavToolbar>
      <template #left>
        <h4 class="pl-4 font-semibold uppercase max-md:hidden md:text-4xl">
          {{ t("thrs.title") }}
        </h4>
        <NavTabs
          v-model:active-module="currentModuleKey"
          class="md:ml-12"
          :modules="modules"
        />
      </template>

      <template #right>
        <ControlActions class="mr-3 max-md:hidden" />
        <SimulationActions class="max-md:hidden" />
      </template>
    </TopNavToolbar>
    <TopNavToolbar class="py-2 transition-all duration-300">
      <template #left>
        <SubNavTabs />
      </template>
    </TopNavToolbar>
  </TopNav>
</template>
