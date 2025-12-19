<script setup lang="ts">
import Button from "@/components/ui/button/Button.vue";
import TopNavToolbar from "@/modules/common/components/top-nav/TopNavToolbar.vue";
import { ref } from "vue";
import { useI18n } from "vue-i18n";
import TopNav from "../../common/components/top-nav/TopNav.vue";
import { AWASelector } from "../components/awa-selector";
import { AWSSelector } from "../components/aws-selector";
import NavTabs from "../components/NavTabs.vue";
import { AWA_VALUES, AWS_VALUES } from "../lib/consts";
import { NumRangeId } from "../types";

const { t } = useI18n();

const twa = ref<NumRangeId>(AWA_VALUES[0].id);
const tws = ref<NumRangeId>(AWS_VALUES[0].id);
</script>

<template>
  <main class="h-svh px-3 pt-[10em] lg:px-4">
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
      <template #right-content>
        <AWASelector
          v-model:model-value="twa"
          class="w-36"
        />
        <AWSSelector
          v-model:model-value="tws"
          class="w-36"
        />
      </template>
    </TopNavToolbar>
  </TopNav>
</template>
