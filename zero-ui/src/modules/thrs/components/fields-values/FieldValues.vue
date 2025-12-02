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

import { ChartDataType, SeriesChart } from "@/modules/common/types";
import { provide, toRef } from "vue";

const props = defineProps<{
  field: string;
  series: SeriesChart<ChartDataType>[];
}>();

provide("fieldSeries", toRef(props, "series"));
provide("field", toRef(props, "field"));
</script>

<template>
  <section
    class="border-border-subtle grid gap-4 rounded-lg border-dashed lg:grid-cols-2 lg:gap-6 2xl:grid-cols-3"
  >
    <slot />
  </section>
</template>
