<script setup lang="ts">
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toRefs } from "vue";
import { useI18n } from "vue-i18n";
import { SIMULATION_TYPES } from "../lib/consts";
import { useSimulationStore } from "../stores/simulation";

const { t } = useI18n();

const { activeSimulationType } = toRefs(useSimulationStore());
</script>

<template>
  <Tabs :model-value="activeSimulationType">
    <TabsList
      class="backdrop-blur-md"
      as="nav"
    >
      <TabsTrigger
        v-for="type in SIMULATION_TYPES"
        :key="type"
        :value="type"
        :disabled="activeSimulationType !== type"
        class="text-sm md:text-base"
      >
        {{ t(`thrs.simulationTypes.${type}`) }}
      </TabsTrigger>
    </TabsList>
  </Tabs>
</template>
