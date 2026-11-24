<script setup lang="ts">
import { GraphQLProvider } from "@/modules/thrapp/mimics/providers";
import { ThrsModules } from "@/modules/thrapp/lib/consts";
import { selectParameter } from "@/modules/thrapp/parameters";
import { useThrsHistory } from "@/modules/thrapp/stores/history";
import { storeToRefs } from "pinia";
import { computed, inject, Ref, useTemplateRef, watch, watchEffect } from "vue";
import { useRoute } from "vue-router";
import { PARAMETERS } from "../router/parameters";

const currentDefinition = inject<Ref<keyof ThrsModules>>("currentModule")!;
const currentParameters = computed(() => PARAMETERS[currentDefinition.value]);

const { activeQuery } = storeToRefs(useThrsHistory());
watchEffect(() => (activeQuery.value = currentParameters.value?.query));

// A manual's parameter link opens this page with `?parameter=<field>` to select it.
const route = useRoute();
const page = useTemplateRef<HTMLElement>("page");
watch(
  [() => route.query.parameter, page],
  ([field, root], _, onCleanup) => {
    if (typeof field === "string" && root) onCleanup(selectParameter(root, field));
  },
  { immediate: true, flush: "post" },
);
</script>
<template>
  <GraphQLProvider>
    <section
      ref="page"
      class="relative h-full"
    >
      <!-- <GridPattern class="absolute top-0 right-0 bottom-0 left-0 h-full w-full" /> -->
      <component :is="currentParameters?.component" />
    </section>
  </GraphQLProvider>
</template>

<style>
@reference "@/assets/index.css";

[data-parameter] {
  @apply scroll-mt-6 outline-2 outline-offset-2 outline-transparent transition-[outline-color] duration-700;
}

/* The PID cards are rounded; a list row keeps square corners for its bottom border. */
[data-parameter]:not(li) {
  @apply rounded-md;
}

[data-parameter][data-selected] {
  @apply outline-brand duration-150;
}
</style>
