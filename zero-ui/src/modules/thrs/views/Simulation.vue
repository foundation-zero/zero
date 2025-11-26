<script setup lang="ts">
import ModuleSimulation from "@/modules/thrs/components/ModuleSimulation.vue";
import ModuleSimulationOutputs from "@/modules/thrs/components/ModuleSimulationOutputs.vue";
import { ModuleDefinition } from "@/modules/thrs/types";

import { DEFINITIONS, QUERIES } from "@/modules/thrs/lib/consts";
import { useClientHandle } from "@urql/vue";
import { computed, inject, Ref } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const { client } = useClientHandle();
const currentDefinition = inject<Ref<keyof typeof DEFINITIONS>>("currentModule")!;
const definition = computed<ModuleDefinition>(() => DEFINITIONS[currentDefinition.value]);
</script>
<template>
  <header class="mb-4 text-3xl capitalize">
    {{ t("views.thrs.hmi.simulation") }}
  </header>

  <ModuleSimulation
    :module="currentDefinition"
    :simulation-inputs="definition.simulation.inputs"
    :query="QUERIES[currentDefinition].simulation.inputs"
    :client="client"
  />

  <header class="mt-8 mb-4 text-3xl capitalize">
    {{ t("views.thrs.hmi.simulationOutputs") }}
  </header>

  <ModuleSimulationOutputs
    :module="currentDefinition"
    :simulation-outputs="definition.simulation.outputs"
    :query="QUERIES[currentDefinition].simulation.outputs"
    :client="client"
  />
</template>
