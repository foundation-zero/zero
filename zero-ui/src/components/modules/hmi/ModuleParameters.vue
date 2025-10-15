<script setup lang="ts" generic="K extends keyof THRSModules">
import { ParametersType } from "@/@types/thrs";
import { THRSDefinitions, THRSModules } from "@/lib/consts";
import { Client } from "@urql/vue";
import { useIntervalFn } from "@vueuse/core";
import { type Component, computed, ref } from "vue";
import { useI18n } from "vue-i18n";
import { queryFor, queryPacked } from ".";
import NumberParameter from "./controls/NumberParameter.vue";
import PIDParameter from "./controls/PIDParameter.vue";

const { t } = useI18n();

const props = defineProps<{
  module: K;
  parameters: THRSDefinitions[K]["parameters"];
  query: string;
  client: Client;
}>();

const COMPONENTS: Record<ParametersType, Component | null> = {
  [ParametersType.Flow]: NumberParameter,
  [ParametersType.Temperature]: NumberParameter,
  [ParametersType.Tuning]: PIDParameter,
};

const parametersValuesQuery = queryFor(props.module, "parameters", props.query);
const parametersFromQuery = queryPacked(props.module, "parameters", parametersValuesQuery);
const parametersFromMutation = ref<THRSModules[K]["parameters"] | null>(null);
const params = computed(
  () =>
    <THRSModules[K]["parameters"] | undefined>(
      (parametersFromMutation.value ?? parametersFromQuery.value.data)
    ),
);

useIntervalFn(
  async () => {
    await parametersFromQuery.value.executeQuery();
    parametersFromMutation.value = null;
  },
  5000,
  { immediateCallback: true },
);

const setControlValues = (newValues: unknown) => {
  parametersFromMutation.value = newValues;
};

const parameterComponents = computed(() => {
  return Object.entries(props.parameters).map(([key, value]) => ({
    ...value,
    key: key as keyof THRSModules[K]["parameters"],
    component: COMPONENTS[value.componentType],
  }));
});
</script>
<template>
  <div v-if="params">
    <header class="mb-2 text-2xl">{{ t("views.thrs.hmi.parameters") }}</header>
    <section class="grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 2xl:grid-cols-6">
      <component
        :is="component.component"
        v-for="component in parameterComponents"
        :key="component.key"
        :model-value="params[component.key]"
        :component-name="String(component.key)"
        :component-type="component.componentType"
        :parameter-values-query="query"
        :module="module"
        @update:control-values="setControlValues"
      />
    </section>
  </div>
</template>
