<script setup lang="ts">
import Button from "@/components/ui/button/Button.vue";
import TopNavToolbar from "@/modules/common/components/top-nav/TopNavToolbar.vue";
import { useI18n } from "vue-i18n";
import TopNav from "../../common/components/top-nav/TopNav.vue";
import NavTabs from "../components/NavTabs.vue";

const { t } = useI18n();
</script>

<template>
  <main class="h-svh pt-[10em] pb-8 max-2xl:px-6 max-lg:px-4 2xl:container 2xl:mx-auto">
    <Suspense>
      <slot />
    </Suspense>
  </main>
  <TopNav>
    <TopNavToolbar>
      <template #left>
        <Button>{{ t("views.loads.main.editSailset") }}</Button>
        <NavTabs class="ml-4" />
      </template>
    </TopNavToolbar>
  </TopNav>
</template>
