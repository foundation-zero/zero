<script
  setup
  lang="ts"
  generic="
    K extends keyof ThrsModules,
    Definitions extends ParameterDefinitions,
    Values extends ExtractAllValues<Definitions>
  "
>
import { QUERIES, ThrsModules } from "@/modules/thrsim/lib/consts.ts";
import {
  ExtractAllValues,
  ParameterDefinitions,
  ParametersType,
} from "@/modules/thrsim/types/index.ts";
import { type Component, computed, toRefs } from "vue";
import { useThrsHistory } from "../stores/history.ts";
import BooleanParameter from "./controls/BooleanParameter.vue";
import ModuleControls from "./controls/ModuleControls.vue";
import NumberParameter from "./controls/NumberParameter.vue";
import PIDParameter from "./controls/PIDParameter.vue";
import RatioParameter from "./controls/RatioParameter.vue";
import NoDataAvailable from "./NoDataAvailable.vue";

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
  [ParametersType.Enabled]: BooleanParameter,
  [ParametersType.Ratio]: RatioParameter,
  [ParametersType.Dutypoint]: RatioParameter,
  [ParametersType.dT]: NumberParameter,
  [ParametersType.Level]: NumberParameter,
  [ParametersType.FlowControl]: RatioParameter,
};
</script>
<template>
  <ModuleControls
    v-if="parametersData"
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
  <NoDataAvailable v-else />
</template>
