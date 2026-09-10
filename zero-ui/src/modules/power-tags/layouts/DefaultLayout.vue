<script setup lang="ts">
import TopNav from "@/modules/common/components/navigation/TopNav.vue";
import TopNavAppLogo from "@/modules/common/components/navigation/TopNavAppLogo.vue";
import TopNavToolbar from "@/modules/common/components/navigation/TopNavToolbar.vue";
import { provideClient } from "@urql/vue";
import { useI18n } from "vue-i18n";
import PanelTabs from "../components/navigation/PanelTabs.vue";
import client from "../graphql/client";

provideClient(client);

const { t } = useI18n();
</script>

<template>
  <main class="h-svh px-3 pt-[8.5em] pb-4 lg:px-4">
    <Suspense>
      <slot />
    </Suspense>
  </main>
  <TopNav class="z-1">
    <TopNavToolbar>
      <template #left-content>
        <TopNavAppLogo>{{ t("apps.powerTags") }}</TopNavAppLogo>
        <PanelTabs class="md:ml-4" />
      </template>
    </TopNavToolbar>
  </TopNav>
</template>
