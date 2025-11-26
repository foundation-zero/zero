<script setup lang="ts">
import NavPills from "@/modules/thrs/components/NavPills.vue";
import Toolbar from "@/modules/thrs/components/Toolbar.vue";
import { useI18n } from "vue-i18n";

import SimulationActions from "@/modules/thrs/components/SimulationActions.vue";

import ControlActions from "@/modules/thrs/components/ControlActions.vue";
import SideNav from "@/modules/thrs/components/SideNav.vue";
import { client } from "@/modules/thrs/graphql/client";
import { THRSModules } from "@/modules/thrs/lib/consts.types";
import { provideClient } from "@urql/vue";
import { useLocalStorage } from "@vueuse/core";
import { provide, ref, watch } from "vue";

// Provide the URL client to inner scope. Pinia stores have their own scope, so they need to manually provide the correct context.
provideClient(client);

const { t } = useI18n();

const modules: Array<keyof THRSModules> = ["thrusters", "pvt", "pcm", "consumers"];
const currentModuleKey = useLocalStorage("hmi:currentModule", modules[0]);

// Temporary hack to force re-mounting of the module view when switching modules
const reset = ref(false);
watch(currentModuleKey, () => {
  reset.value = true;
  setTimeout(() => {
    reset.value = false;
  }, 0);
});

provide("currentModule", currentModuleKey);
</script>

<template>
  <main class="h-svh pt-[128px] pb-8 pl-[266px]">
    <SideNav class="fixed left-4 w-[250px] shrink-0" />
    <Suspense>
      <slot v-if="!reset" />
    </Suspense>
  </main>
  <nav class="fixed top-0 right-0 left-0 backdrop-blur-md">
    <Toolbar class="border-border-subtle items-center border-b px-4">
      <template #left>
        <div class="flex items-center">
          <h4 class="pl-4 text-4xl font-semibold uppercase">{{ t("labels.hmi") }}</h4>
          <NavPills
            v-model:active-module="currentModuleKey"
            class="ml-12 h-full"
            :modules="modules"
          />
        </div>
      </template>

      <template #right>
        <ControlActions class="mr-3" />
        <SimulationActions />
      </template>
    </Toolbar>
  </nav>
</template>
