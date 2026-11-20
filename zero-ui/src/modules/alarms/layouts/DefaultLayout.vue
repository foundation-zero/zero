<script setup lang="ts">
import TopNav from "@/modules/common/components/navigation/TopNav.vue";
import TopNavAppLogo from "@/modules/common/components/navigation/TopNavAppLogo.vue";
import TopNavToolbar from "@/modules/common/components/navigation/TopNavToolbar.vue";
import { useI18n } from "vue-i18n";

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
        <TopNavAppLogo>{{ t("apps.alarms") }}</TopNavAppLogo>
      </template>
    </TopNavToolbar>
  </TopNav>
</template>
