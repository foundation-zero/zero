<script setup lang="ts">
import ModuleParameters from "@/components/modules/hmi/ModuleParameters.vue";

import { DEFINITIONS, QUERIES } from "@/lib/consts";
import { objectFilter } from "@/lib/utils";
import { useClientHandle } from "@urql/vue";
import { computed, ref } from "vue";
import { useI18n } from "vue-i18n";

const { t } = useI18n();

const { client } = useClientHandle();
const currentDefinition = ref<keyof typeof DEFINITIONS>("thrusters");
const definition = computed(() => DEFINITIONS[currentDefinition.value]);

type Parameters = typeof definition.value.parameters;

const regularParams = computed(
  () =>
    objectFilter(
      definition.value.parameters,
      ([, { componentType }]) => componentType !== "tuning",
    ) as Parameters,
);

const tuningParams = computed(
  () =>
    objectFilter(
      definition.value.parameters,
      ([, { componentType }]) => componentType === "tuning",
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
