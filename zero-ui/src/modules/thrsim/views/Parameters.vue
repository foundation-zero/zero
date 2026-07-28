<script setup lang="ts">
import { ModuleDefinition, ParametersType } from "@/modules/thrsim/types";

import ParametersControls from "@/modules/thrs/components/ParametersControls.vue";
import { DEFINITIONS } from "@/modules/thrsim/lib/consts";
import { objectFilter } from "@common/lib/utils";
import { computed, inject, Ref } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

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
    {{ t("thrs.views.parameters.title") }}
  </header>

  <ParametersControls
    :module="currentDefinition"
    :definition="regularParams"
  />

  <header class="mt-8 mb-4 text-3xl capitalize">
    {{ t("thrs.views.parameters.tuning") }}
  </header>

  <ParametersControls
    :module="currentDefinition"
    :definition="tuningParams"
  />
</template>
