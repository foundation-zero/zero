<script setup lang="ts" generic="Definitions extends SimulationDefinitions">
import {
  SIMULATION,
  SIMULATION_INPUT_QUERIES,
  THRSSimulationType,
} from "@/modules/thrs/lib/consts";
import { SimulationComponentType, SimulationDefinitions } from "@/modules/thrs/types";
import { type Component, computed, toRefs } from "vue";
import { useThrsHistory } from "../stores/history";
import BoundaryControl from "./controls/BoundaryControl.vue";
import ModuleControls from "./controls/ModuleControls.vue";
import PcsControl from "./controls/PcsControl.vue";
import TemperatureControl from "./controls/TemperatureControl.vue";
import ThrustersControl from "./controls/ThrustersControl.vue";

const COMPONENTS: Record<SimulationComponentType, Component | null> = {
  [SimulationComponentType.Thruster]: ThrustersControl,
  [SimulationComponentType.Boundary]: BoundaryControl,
  [SimulationComponentType.Flow]: null,
  [SimulationComponentType.Temperature]: TemperatureControl,
  [SimulationComponentType.Pcs]: PcsControl,
  [SimulationComponentType.HeatSource]: null,
};

const { data } = toRefs(useThrsHistory());

const props = defineProps<{ type: THRSSimulationType }>();

const definition = computed(() => SIMULATION.inputs[props.type] as SimulationDefinitions);

const simulationInputsData = computed(() => data.value?.simulation.inputs);
</script>
<template>
  <ModuleControls
    v-if="definition && simulationInputsData"
    :controls="definition"
    :data="simulationInputsData"
    :disabled="false"
  >
    <template #default="{ componentName, componentDefinition, setControlValues, values }">
      <component
        :is="COMPONENTS[componentDefinition.componentType]"
        :values="values"
        :query="SIMULATION_INPUT_QUERIES[type]"
        :component-name="componentName"
        :component-type="componentDefinition.componentType"
        :simulation="type"
        @update:control-values="setControlValues"
      />
    </template>
  </ModuleControls>
</template>
