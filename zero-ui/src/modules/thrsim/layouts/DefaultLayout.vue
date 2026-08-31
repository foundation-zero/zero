<script setup lang="ts">
import NavTabs from "@/modules/thrsim/components/NavTabs.vue";
import { useI18n } from "vue-i18n";

import SimulationActions from "@/modules/thrsim/components/SimulationActions.vue";

import TopNav from "@/modules/common/components/navigation/TopNav.vue";
import TopNavAppLogo from "@/modules/common/components/navigation/TopNavAppLogo.vue";
import TopNavToolbar from "@/modules/common/components/navigation/TopNavToolbar.vue";
import { client } from "@/modules/thrsim/graphql/client.ts";
import { ThrsModules } from "@/modules/thrsim/lib/consts.types.ts";
import { provideClient } from "@urql/vue";
import { computed, provide } from "vue";
import { useRoute } from "vue-router";
import ControlActions from "../components/ControlActions.vue";
import SimulationTabs from "../components/SimulationTabs.vue";
import SubNavTabs from "../components/SubNavTabs.vue";

// Provide the URL client to inner scope. Pinia stores have their own scope, so they need to manually provide the correct context.
provideClient(client);

const { t } = useI18n();

const currentRoute = useRoute();
const modules: Array<keyof ThrsModules> = [
  "thrusters",
  "pvt",
  "pcm",
  "consumers",
  "adsorption",
  "drives",
  "dhw",
  "dc",
];
const currentModuleKey = computed(() => (currentRoute.params.module as string) ?? "simulation");

provide("currentModule", currentModuleKey);
</script>

<template>
  <main class="h-svh pt-[12em]">
    <Suspense>
      <article class="h-full px-4 pb-4 md:px-6 md:pb-6">
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
        <RouterLink
          :to="{ name: 'thrsim/simulation' }"
          class="flex items-center"
        >
          <span
            class="hover:text-foreground text-disabled-foreground font-headers cursor-pointer rounded-none px-3 py-2 text-sm font-medium uppercase"
            :class="{
              'text-foreground border-attention border-b':
                currentRoute.name === 'thrsim/simulation',
            }"
          >
            {{ t("thrs.views.simulation.title") }}
          </span>
        </RouterLink>
        <SimulationActions class="max-md:hidden" />
      </template>
    </TopNavToolbar>
    <TopNavToolbar class="py-1 transition-all duration-300 md:py-2">
      <template #left>
        <SubNavTabs v-if="currentRoute.params.module" />
        <SimulationTabs v-else />
      </template>
      <template
        v-if="currentRoute.params.module"
        #right
      >
        <ControlActions :active-module="currentModuleKey" />
      </template>
    </TopNavToolbar>
  </TopNav>
</template>
