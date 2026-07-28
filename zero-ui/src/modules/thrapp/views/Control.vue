<script setup lang="ts">
import GridPattern from "@/modules/thrapp/mimics/modules/GridPattern.vue";
import { GraphQLProvider } from "@/modules/thrapp/mimics/providers";
import { DEFINITIONS } from "@/modules/thrsim/lib/consts";
import { defineAsyncComponent, inject, Ref } from "vue";

const currentDefinition = inject<Ref<keyof typeof DEFINITIONS>>("currentModule")!;
const DHWParameters = defineAsyncComponent(
  () => import("@/modules/thrapp/components/module-parameters/dhw/DHWParameters.vue"),
);
</script>
<template>
  <GraphQLProvider>
    <section class="relative h-full">
      <GridPattern class="absolute top-0 right-0 bottom-0 left-0 h-full w-full" />
      <DHWParameters
        v-if="currentDefinition === 'dhw'"
        class="relative"
      />
    </section>
  </GraphQLProvider>
</template>
