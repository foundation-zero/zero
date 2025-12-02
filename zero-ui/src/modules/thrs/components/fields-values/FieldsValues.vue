<script
  setup
  lang="ts"
  generic="
    K extends keyof THRSModules,
    Definitions extends SchemaDefinitions<SchemaDefinition<unknown>>
  "
>
import { THRSModules } from "@/modules/thrs/lib/consts";
import { SchemaDefinition, SchemaDefinitions } from "@/modules/thrs/types";

import { computed, ref } from "vue";
import { FieldSeries, provideContext } from ".";
import { useThrsHistory } from "../../stores/history";
import FieldValues from "./FieldValues.vue";

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

const selected = ref<string[]>([]);
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
