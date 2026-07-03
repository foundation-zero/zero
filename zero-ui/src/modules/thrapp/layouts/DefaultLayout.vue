<script setup lang="ts">
import NavTabs from "@/modules/thrapp/components/navigation/MainNav.vue";
import { useI18n } from "vue-i18n";

import TopNav from "@/modules/common/components/navigation/TopNav.vue";
import TopNavAppLogo from "@/modules/common/components/navigation/TopNavAppLogo.vue";
import TopNavToolbar from "@/modules/common/components/navigation/TopNavToolbar.vue";
import { client } from "@/modules/thrs/graphql/client";
import { ThrsModules } from "@/modules/thrs/lib/consts.types";
import { provideClient } from "@urql/vue";
import { computed, provide } from "vue";
import { useRoute } from "vue-router";

// Provide the URL client to inner scope. Pinia stores have their own scope, so they need to manually provide the correct context.
provideClient(client);

const { t } = useI18n();

const currentRoute = useRoute();
const modules: Array<keyof ThrsModules> = ["dhw", "thrusters", "pvt", "pcm", "consumers"];
const currentModuleKey = computed(() => currentRoute.params.module as string);

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
          {{ t("apps.thrapp") }}
        </TopNavAppLogo>

        <NavTabs
          :active-module="currentModuleKey"
          class="md:ml-4"
          :modules="modules"
        />
      </template>
    </TopNavToolbar>
    <TopNavToolbar class="py-1 transition-all duration-300 md:py-2">
      <template
        v-if="currentRoute.meta.toolbarLeft"
        #left
      >
        <component
          :is="currentRoute.meta.toolbarLeft"
          :modules="modules"
          :active-module="currentModuleKey"
        />
      </template>
      <template
        v-if="currentRoute.meta.toolbarRight"
        #right
      >
        <component
          :is="currentRoute.meta.toolbarRight"
          :modules="modules"
          :active-module="currentModuleKey"
        />
      </template>
    </TopNavToolbar>
  </TopNav>
</template>
