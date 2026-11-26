<script setup lang="ts">
import NavTabs from "@/modules/thrsim/components/NavTabs.vue";
import { useI18n } from "vue-i18n";

import SimulationActions from "@/modules/thrsim/components/SimulationActions.vue";

import TopNav from "@/modules/common/components/navigation/TopNav.vue";
import TopNavAppLogo from "@/modules/common/components/navigation/TopNavAppLogo.vue";
import TopNavToolbar from "@/modules/common/components/navigation/TopNavToolbar.vue";
import ControlActions from "@/modules/thrapp/components/control-actions/ControlActions.vue";
import { getControlModule } from "@/modules/thrapp/components/sub-navigation";
import { mqttGraphqlClient } from "@/modules/thrapp/graphql/client";
import { ControlledModule } from "@/modules/thrapp/lib/consts";
import { MimicKey } from "@/modules/thrapp/router/mimics";
import { provideClient } from "@urql/vue";
import { computed, onMounted, onUnmounted, provide } from "vue";
import { useRoute } from "vue-router";
import SimulationTabs from "../components/SimulationTabs.vue";
import SubNavTabs from "../components/SubNavTabs.vue";
import { useSimulationStore } from "../stores/simulation";

// Provide the URL client to inner scope. Pinia stores have their own scope, so they need to manually provide the correct context.
provideClient(mqttGraphqlClient);

const { t } = useI18n();

const currentRoute = useRoute();
const modules: Array<MimicKey> = [
  "dhw",
  "thrusters",
  "pvt",
  "pvt-main",
  "pvt-owners",
  "pcm",
  "dc",
  "dc-aft",
  "dc-ugrid",
  "dc-fwd",
  "drives",
  "drives-shorepower",
  "adsorption",
];
const currentModuleKey = computed(() => (currentRoute.params.module as string) ?? "simulation");

// The controls, monitoring and parameters views show a sub-mimic's parent module (e.g. dc for
// dc-aft); only the mimic view reads the sub-mimic from the route.
const currentControlModule = computed(() => getControlModule(currentModuleKey.value as MimicKey));

provide("currentModule", currentControlModule);

const { startPolling, stopPolling } = useSimulationStore();

onMounted(startPolling);
onUnmounted(stopPolling);
</script>

<template>
  <main class="h-svh pt-[12em]">
    <Suspense>
      <article class="flex h-full flex-col px-4 md:px-6 md:pb-6">
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
        <ControlActions :active-module="currentControlModule as ControlledModule" />
      </template>
    </TopNavToolbar>
  </TopNav>
</template>
