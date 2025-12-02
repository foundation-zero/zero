<script
  setup
  lang="ts"
  generic="
    K extends keyof THRSModules,
    Definitions extends ParameterDefinitions,
    Values extends ExtractAllValues<Definitions>
  "
>
import { QUERIES, THRSModules } from "@/modules/thrs/lib/consts";
import { ExtractAllValues, ParameterDefinitions, ParametersType } from "@/modules/thrs/types";
import { type Component, computed, toRefs } from "vue";
import { useThrsHistory } from "../stores/history";
import ModuleControls from "./controls/ModuleControls.vue";
import NumberParameter from "./controls/NumberParameter.vue";
import PIDParameter from "./controls/PIDParameter.vue";

const props = defineProps<{
  module: K;
  definition: Definitions;
}>();

const { data } = toRefs(useThrsHistory());

const parametersData = computed(
  () => data.value?.modules[props.module]?.parameters as Values | undefined,
);

const COMPONENTS: Record<ParametersType, Component | null> = {
  [ParametersType.Flow]: NumberParameter,
  [ParametersType.Temperature]: NumberParameter,
  [ParametersType.Tuning]: PIDParameter,
};
</script>
<template>
  <ModuleControls
    :controls="definition"
    :data="parametersData"
    :disabled="false"
  >
    <template #default="{ componentName, componentDefinition, setControlValues, values }">
      <component
        :is="COMPONENTS[componentDefinition.componentType]"
        :definition="componentDefinition"
        :module="module"
        :model-value="values"
        :query="QUERIES[module].parameters"
        :component-name="componentName"
        :component-type="componentDefinition.componentType"
        @update:control-values="setControlValues"
      />
    </template>
  </ModuleControls>
</template>
