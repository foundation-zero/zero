<script
  setup
  lang="ts"
  generic="
    K extends HistoryRootKey,
    Definitions extends SchemaDefinitions<SchemaDefinition<unknown>>
  "
>
import { SchemaDefinition, SchemaDefinitions } from "@/modules/thrsim/types/index.ts";

import { useLocalStorage } from "@vueuse/core";
import { computed } from "vue";
import { HistoryRootKey, useThrsHistory } from "../../stores/history.ts";
import FieldValues from "./FieldValues.vue";
import { FieldSeries, provideContext } from "./index.ts";

const props = defineProps<{
  module: K;
  definitions: Definitions[];
  fields: string[];
}>();

const { useHistory } = useThrsHistory();

const series = computed(() =>
  props.fields.map<FieldSeries>((field) => [
    field,
    props.definitions
      .flatMap((definition) => useHistory(props.module, field, definition).value)
      .filter((serie, index, series) => index === series.findIndex((s) => s.name === serie.name)),
  ]),
);

const selected = useLocalStorage<string[]>(
  `thrs-${props.module}-fields-values-selected`,
  props.fields.slice(),
);

const activeSeries = computed(() =>
  series.value.filter(([field]) => selected.value.includes(field)),
);

provideContext({
  series,
  selected,
  activeSeries,
});
</script>
<template>
  <ul class="grid gap-4 lg:gap-6">
    <slot />
    <FieldValues
      v-for="[field, fieldSeries] in activeSeries"
      :key="field"
      :series="fieldSeries"
      :field="field"
    >
      <slot
        name="field"
        v-bind="{ field, series: fieldSeries }"
      />
    </FieldValues>
  </ul>
</template>
