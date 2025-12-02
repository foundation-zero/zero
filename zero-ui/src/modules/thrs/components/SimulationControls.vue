<script
  setup
  lang="ts"
  generic="
    K extends keyof THRSModules,
    Definitions extends SimulationDefinitions,
    Values extends ExtractAllValues<Definitions>
  "
>
import { QUERIES, THRSModules } from "@/modules/thrs/lib/consts";
import {
  ExtractAllValues,
  SimulationComponentType,
  SimulationDefinitions,
} from "@/modules/thrs/types";
import { type Component, computed, toRefs } from "vue";
import { useThrsHistory } from "../stores/history";
import BoundaryControl from "./controls/BoundaryControl.vue";
import ModuleControls from "./controls/ModuleControls.vue";
import PcsControl from "./controls/PcsControl.vue";
import TemperatureControl from "./controls/TemperatureControl.vue";
import ThrustersControl from "./controls/ThrustersControl.vue";

const props = defineProps<{
  module: K;
  definition: Definitions;
}>();

const COMPONENTS: Record<SimulationComponentType, Component | null> = {
  [SimulationComponentType.Thruster]: ThrustersControl,
  [SimulationComponentType.Boundary]: BoundaryControl,
  [SimulationComponentType.Flow]: null,
  [SimulationComponentType.Temperature]: TemperatureControl,
  [SimulationComponentType.Pcs]: PcsControl,
  [SimulationComponentType.HeatSource]: null,
};

const { data } = toRefs(useThrsHistory());

const simulationInputsData = computed(
  () => data.value?.modules[props.module]?.simulation.inputs as Values | undefined,
);
</script>
<template>
  <ModuleControls
    :controls="definition"
    :data="simulationInputsData"
    :disabled="false"
  >
    <template #default="{ componentName, componentDefinition, setControlValues, values }">
      <component
        :is="COMPONENTS[componentDefinition.componentType]"
        :values="values"
        :query="QUERIES[module].simulation.inputs"
        :component-name="componentName"
        :component-type="componentDefinition.componentType"
        :module="module"
        @update:control-values="setControlValues"
      />
    </template>
  </ModuleControls>
</template>
