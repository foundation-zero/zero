<script
  setup
  lang="ts"
  generic="
    K extends keyof THRSModules,
    Definitions extends ParameterDefinitions = THRSDefinitions[K]['parameters'],
    Values extends ExtractParameterValues<Definitions> = ExtractParameterValues<Definitions>
  "
>
import { ExtractParameterValues, ParameterDefinitions, ParametersType } from "@/@types/thrs";
import { THRSDefinitions, THRSModules } from "@/lib/consts";
import { Client } from "@urql/vue";
import { useIntervalFn } from "@vueuse/core";
import { type Component, computed, ref } from "vue";
import { queryDeep, queryFor } from ".";
import NumberParameter from "./controls/NumberParameter.vue";
import PIDParameter from "./controls/PIDParameter.vue";

const props = defineProps<{
  module: K;
  parameters: Definitions;
  query: string;
  client: Client;
}>();

const COMPONENTS: Record<ParametersType, Component | null> = {
  [ParametersType.Flow]: NumberParameter,
  [ParametersType.Temperature]: NumberParameter,
  [ParametersType.Tuning]: PIDParameter,
};

const parametersValuesQuery = queryFor(props.module, "parameters", props.query);
const parametersFromQuery = queryDeep(
  parametersValuesQuery,
  (data) => data?.modules?.[props.module]?.parameters as Values | undefined,
);
const parametersFromMutation = ref<Values | null>(null);
const params = computed(
  () => (parametersFromMutation.value ?? parametersFromQuery.data.value) as Values,
);

useIntervalFn(
  async () => {
    await parametersFromQuery.update();
    parametersFromMutation.value = null;
  },
  5000,
  { immediateCallback: true },
);

const setControlValues = (newValues: Values) => {
  parametersFromMutation.value = newValues;
};

const parameterComponents = computed(() => {
  return Object.entries(props.parameters).map(([key, value]) => ({
    ...value,
    key: key as keyof Values,
    component: COMPONENTS[value.componentType],
  }));
});
</script>
<template>
  <section
    v-if="params"
    class="grid gap-6 md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4"
  >
    <component
      :is="component.component"
      v-for="component in parameterComponents"
      :key="component.key"
      :model-value="params[component.key]"
      :component-name="String(component.key)"
      :component-type="component.componentType"
      :query="query"
      :module="module"
      @update:control-values="setControlValues"
    />
  </section>
</template>
