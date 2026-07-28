<script
  setup
  lang="ts"
  generic="
    Definitions extends SchemaDefinitions<SchemaDefinition<string>>,
    Values extends ExtractAllValues<Definitions> = ExtractAllValues<Definitions>
  "
>
import { ExtractAllValues, SchemaDefinition, SchemaDefinitions } from "@/modules/thrsim/types";

import { objectEntries } from "@vueuse/core";
import { computed, ref, toRefs, watch } from "vue";
import { useThrsHistory } from "../../stores/history";

const props = defineProps<{
  controls: Definitions;
  disabled?: boolean;
  data: Values | undefined;
}>();

const controlValuesFromMutation = ref<Values | null>(null);
const controlValues = computed(() => (controlValuesFromMutation.value ?? props.data) as Values);
const { lastUpdate } = toRefs(useThrsHistory());

watch(lastUpdate, (next, prev) => {
  if (next !== prev) {
    controlValuesFromMutation.value = null;
  }
});

const setControlValues = (newValues: Values) => {
  controlValuesFromMutation.value = newValues;
};
</script>
<template>
  <section
    v-if="controlValues"
    class="mb-4 grid gap-6 sm:grid-cols-2 lg:grid-cols-3 2xl:grid-cols-4"
    :class="{ 'pointer-events-none cursor-not-allowed opacity-50': disabled }"
  >
    <slot
      v-for="[key, control] of objectEntries(controls)"
      :key="key"
      v-bind="{
        componentName: key,
        componentDefinition: control,
        setControlValues,
        values: controlValues[key as keyof Values],
      }"
    ></slot>
  </section>
</template>
