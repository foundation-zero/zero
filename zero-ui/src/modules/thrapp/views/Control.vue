<script setup lang="ts">
import { GraphQLProvider } from "@/modules/thrapp/mimics/providers";
import { ThrsModules } from "@/modules/thrapp/lib/consts";
import { useThrsHistory } from "@/modules/thrapp/stores/history";
import { storeToRefs } from "pinia";
import { computed, inject, Ref, watchEffect } from "vue";
import { PARAMETERS } from "../router/parameters";

const currentDefinition = inject<Ref<keyof ThrsModules>>("currentModule")!;
const currentParameters = computed(() => PARAMETERS[currentDefinition.value]);

const { activeQuery } = storeToRefs(useThrsHistory());
watchEffect(() => (activeQuery.value = currentParameters.value?.query));
</script>
<template>
  <GraphQLProvider>
    <section class="relative h-full">
      <!-- <GridPattern class="absolute top-0 right-0 bottom-0 left-0 h-full w-full" /> -->
      <component :is="currentParameters?.component" />
    </section>
  </GraphQLProvider>
</template>
