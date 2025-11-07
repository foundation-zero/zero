<script setup lang="ts">
import { ModuleDefinition, ParametersType } from "@/@types/thrs";
import ModuleParameters from "@/components/modules/hmi/ModuleParameters.vue";

import { DEFINITIONS, QUERIES } from "@/lib/consts";
import { objectFilter } from "@/lib/utils";
import { useClientHandle } from "@urql/vue";
import { computed, inject, Ref } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const { client } = useClientHandle();

const currentDefinition = inject<Ref<keyof typeof DEFINITIONS>>("currentModule")!;
const definition = computed<ModuleDefinition>(() => DEFINITIONS[currentDefinition.value]);

type Parameters = typeof definition.value.parameters;

const regularParams = computed(
  () =>
    objectFilter(
      definition.value.parameters,
      ([, { componentType }]) => componentType !== ParametersType.Tuning,
    ) as Parameters,
);

const tuningParams = computed(
  () =>
    objectFilter(
      definition.value.parameters,
      ([, { componentType }]) => componentType === ParametersType.Tuning,
    ) as Parameters,
);
</script>
<template>
  <header class="mb-4 text-3xl capitalize">
    {{ t("views.thrs.hmi.parameters") }}
  </header>

  <ModuleParameters
    :module="currentDefinition"
    :parameters="regularParams"
    :query="QUERIES[currentDefinition].parameters"
    :client="client"
  />

  <header class="mt-8 mb-4 text-3xl capitalize">
    {{ t("views.thrs.hmi.tuning") }}
  </header>

  <ModuleParameters
    :module="currentDefinition"
    :parameters="tuningParams"
    :query="QUERIES[currentDefinition].parameters"
    :client="client"
  />
</template>
