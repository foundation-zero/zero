<script setup lang="ts">
import TopNavToolbar from "@/modules/common/components/navigation/TopNavToolbar.vue";
import { toRefs } from "vue";
import TopNav from "../../common/components/navigation/TopNav.vue";
import { AWASelector } from "../components/awa-selector";
import { AWSSelector } from "../components/aws-selector";
import { CardTypeToggle } from "../components/card-type-toggle";
import NavTabs from "../components/NavTabs.vue";
import SailSelector from "../components/SailSelector.vue";
import SelectedLoadCaseLabel from "../components/SelectedLoadCaseLabel.vue";
import SystemAlerts from "../components/system-alerts/SystemAlerts.vue";
import { WindConditions, WindConditionsLockTrigger } from "../components/wind-conditions";
import { useVariablesStore } from "../stores/variables";

const { selectedAWA, selectedAWS, selectedCardType, currentAWA, currentAWS, selectedLoadCase } =
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
    <template #right-content>
      <SystemAlerts />
    </template>
    <TopNavToolbar>
      <template #left>
        <SailSelector />
        <NavTabs class="ml-4" />
      </template>
      <template #right-content>
        <div
          class="grid grid-cols-[auto_9rem_9rem_auto_auto] items-center justify-end gap-x-2 gap-y-0.5 py-1"
        >
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
          <div class="col-span-4 col-start-2 justify-self-start pt-0.5">
            <SelectedLoadCaseLabel :load-case="selectedLoadCase" />
          </div>
        </div>
      </template>
    </TopNavToolbar>
  </TopNav>
</template>
