<script setup lang="ts">
import ModuleControls from "@/components/modules/hmi/ModuleControls.vue";
import ModuleParameters from "@/components/modules/hmi/ModuleParameters.vue";
import ModuleSensors from "@/components/modules/hmi/ModuleSensors.vue";
import ModuleSimulation from "@/components/modules/hmi/ModuleSimulation.vue";
import ModuleSimulationOutputs from "@/components/modules/hmi/ModuleSimulationOutputs.vue";

import { DEFINITIONS, QUERIES } from "@/lib/consts";
import { useClientHandle } from "@urql/vue";
import { computed, ref } from "vue";

const { client } = useClientHandle();
const currentDefinition = ref<keyof typeof DEFINITIONS>("thrusters");
const definition = computed(() => DEFINITIONS[currentDefinition.value]);
</script>
<template>
  <main class="pb-8">
    <article class="grid gap-8 px-4">
      <ModuleControls
        :module="currentDefinition"
        :controls="definition.controlValues"
        :query="QUERIES[currentDefinition].controlValues"
        :client="client"
      />

      <ModuleSimulation
        :module="currentDefinition"
        :simulation-controls="definition.simulation"
        :query="QUERIES[currentDefinition].simulation.inputs"
        :client="client"
      />

      <ModuleSimulationOutputs
        :module="currentDefinition"
        :simulation-controls="definition.simulation"
        :query="QUERIES[currentDefinition].simulation.outputs"
        :client="client"
      />

      <ModuleParameters
        :module="currentDefinition"
        :parameters="definition.parameters"
        :query="QUERIES[currentDefinition].parameters"
        :client="client"
      />

      <ModuleSensors
        :module="currentDefinition"
        :sensors="definition.sensorValues"
        :query="QUERIES[currentDefinition].sensorValues"
        :client="client"
      />
    </article>
  </main>
</template>
