<script setup lang="ts">
import TopNavToolbar from "@/modules/common/components/top-nav/TopNavToolbar.vue";
import { toRefs } from "vue";
import TopNav from "../../common/components/top-nav/TopNav.vue";
import { AWASelector } from "../components/awa-selector";
import { AWSSelector } from "../components/aws-selector";
import NavTabs from "../components/NavTabs.vue";
import SailSelector from "../components/SailSelector.vue";
import { useVariablesStore } from "../stores/variables";

const { selectedAWA, selectedAWS } = toRefs(useVariablesStore());
const { setAWA, setAWS } = useVariablesStore();
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
        <SailSelector />
        <NavTabs class="ml-4" />
      </template>
      <template #right-content>
        <AWASelector
          :model-value="selectedAWA"
          class="w-36"
          @update:model-value="setAWA"
        />
        <AWSSelector
          :model-value="selectedAWS"
          class="w-36"
          @update:model-value="setAWS"
        />
      </template>
    </TopNavToolbar>
  </TopNav>
</template>
