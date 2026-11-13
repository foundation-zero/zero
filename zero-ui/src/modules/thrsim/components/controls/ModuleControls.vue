<script
  setup
  lang="ts"
  generic="
    Definitions extends SchemaDefinitions<SchemaDefinition<string>>,
    Values extends ExtractAllValues<Definitions> = ExtractAllValues<Definitions>
  "
>
import { SchemaDefinition, SchemaDefinitions } from "@/modules/thrapp/types/thrs";
import { ExtractAllValues } from "@/modules/thrsim/types";

import { objectEntries } from "@vueuse/core";

defineProps<{
  controls: Definitions;
  disabled?: boolean;
  data: Values | undefined;
}>();
</script>
<template>
  <section
    v-if="data"
    class="mb-4 grid gap-6 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4"
    :class="{ 'pointer-events-none cursor-not-allowed opacity-50': disabled }"
  >
    <slot
      v-for="[key, control] of objectEntries(controls)"
      :key="key"
      v-bind="{
        componentName: key,
        componentDefinition: control,
        values: data[key as keyof Values],
      }"
    ></slot>
  </section>
</template>
