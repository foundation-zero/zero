<script setup lang="ts">
import TopNavToolbar from "@/modules/common/components/top-nav/TopNavToolbar.vue";
import { toRefs } from "vue";
import TopNav from "../../common/components/top-nav/TopNav.vue";
import { AWASelector } from "../components/awa-selector";
import { AWSSelector } from "../components/aws-selector";
import { CardTypeToggle } from "../components/card-type-toggle";
import NavTabs from "../components/NavTabs.vue";
import SailSelector from "../components/SailSelector.vue";
import { WindConditions, WindConditionsLockTrigger } from "../components/wind-conditions";
import { useVariablesStore } from "../stores/variables";

const { selectedAWA, selectedAWS, selectedCardType, currentAWA, currentAWS } =
  toRefs(useVariablesStore());
const { setAWA, setAWS, setCardType, lockWindConditions } = useVariablesStore();
</script>

<template>
  <main class="h-svh px-3 pt-[8.5em] lg:px-4">
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
        <CardTypeToggle
          v-model="selectedCardType"
          @update:model-value="setCardType"
        />
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
        <WindConditionsLockTrigger @trigger="lockWindConditions" />
        <WindConditions
          :awa="currentAWA"
          :aws="currentAWS"
        />
      </template>
    </TopNavToolbar>
  </TopNav>
</template>
