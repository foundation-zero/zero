<script setup lang="ts">
import ModuleControls from "@/components/modules/hmi/ModuleControls.vue";
import ModuleParameters from "@/components/modules/hmi/ModuleParameters.vue";
import ModuleSensors from "@/components/modules/hmi/ModuleSensors.vue";
import { DEFINITIONS, QUERIES } from "@/lib/consts";
import { Client, fetchExchange, provideClient } from "@urql/vue";
import { computed, ref } from "vue";

const client = new Client({
  url: "/api/thrs/graphql",
  exchanges: [fetchExchange],
});

provideClient(client);

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
