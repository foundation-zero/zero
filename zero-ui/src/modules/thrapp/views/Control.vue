<script setup lang="ts">
import { GraphQLProvider } from "@/modules/thrapp/mimics/providers";
import { ThrsModules } from "@/modules/thrsim/lib/consts";
import { inject, Ref } from "vue";
import { PARAMETERS } from "../router/parameters";

const currentDefinition = inject<Ref<keyof ThrsModules>>("currentModule")!;
</script>
<template>
  <GraphQLProvider>
    <section class="relative h-full">
      <!-- <GridPattern class="absolute top-0 right-0 bottom-0 left-0 h-full w-full" /> -->
      <component :is="PARAMETERS[currentDefinition]" />
    </section>
  </GraphQLProvider>
</template>
