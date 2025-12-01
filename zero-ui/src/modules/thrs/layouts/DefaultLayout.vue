<script setup lang="ts">
import NavTabs from "@/modules/thrs/components/NavTabs.vue";
import { useI18n } from "vue-i18n";

import SimulationActions from "@/modules/thrs/components/SimulationActions.vue";

import { useScrollOffset } from "@/modules/common/components/top-nav";
import TopNav from "@/modules/common/components/top-nav/TopNav.vue";
import TopNavToolbar from "@/modules/common/components/top-nav/TopNavToolbar.vue";
import ControlActions from "@/modules/thrs/components/ControlActions.vue";
import SideNav from "@/modules/thrs/components/SideNav.vue";
import { client } from "@/modules/thrs/graphql/client";
import { THRSModules } from "@/modules/thrs/lib/consts.types";
import { provideClient } from "@urql/vue";
import { useLocalStorage } from "@vueuse/core";
import { provide } from "vue";

// Provide the URL client to inner scope. Pinia stores have their own scope, so they need to manually provide the correct context.
provideClient(client);

const { t } = useI18n();
const scrollOffset = useScrollOffset();

const modules: Array<keyof THRSModules> = ["thrusters", "pvt", "pcm", "consumers"];
const currentModuleKey = useLocalStorage("hmi:currentModule", modules[0]);

// Temporary hack to force re-mounting of the module view when switching modules

provide("currentModule", currentModuleKey);
</script>

<template>
  <main class="h-svh pt-[10em] pb-8 pl-[266px]">
    <SideNav
      class="fixed left-4 w-[250px] shrink-0"
      :style="{ marginTop: scrollOffset }"
    />
    <Suspense>
      <article class="px-6 pb-8">
        <slot />
      </article>
    </Suspense>
  </main>
  <TopNav>
    <TopNavToolbar>
      <template #left>
        <h4 class="pl-4 text-4xl font-semibold uppercase">{{ t("thrs.title") }}</h4>
        <NavTabs
          v-model:active-module="currentModuleKey"
          class="ml-12"
          :modules="modules"
        />
      </template>

      <template #right>
        <ControlActions class="mr-3" />
        <SimulationActions />
      </template>
    </TopNavToolbar>
  </TopNav>
</template>
