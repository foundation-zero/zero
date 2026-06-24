<script setup lang="ts" generic="Definitions extends SimulationDefinitions">
import {
  SIMULATION,
  SIMULATION_INPUT_QUERIES,
  ThrsSimulationType,
} from "@/modules/thrs/lib/consts";
import {
  ExtractAllValues,
  SimulationComponentType,
  SimulationDefinitions,
} from "@/modules/thrs/types";
import { type Component, computed, toRefs } from "vue";
import { useThrsHistory } from "../stores/history";
import BoundaryControl from "./controls/BoundaryControl.vue";
import FlowControl from "./controls/FlowControl.vue";
import HeatSourceControl from "./controls/HeatSourceControl.vue";
import HvacControl from "./controls/HvacControl.vue";
import ModuleControls from "./controls/ModuleControls.vue";
import OverpressureTemperatureControl from "./controls/OverpressureTemperatureControl.vue";
import PcsControl from "./controls/PcsControl.vue";
import TemperatureControl from "./controls/TemperatureControl.vue";
import ThrustersControl from "./controls/ThrustersControl.vue";

const COMPONENTS: Record<SimulationComponentType, Component | null> = {
  [SimulationComponentType.Thruster]: ThrustersControl,
  [SimulationComponentType.Boundary]: BoundaryControl,
  [SimulationComponentType.Flow]: FlowControl,
  [SimulationComponentType.Temperature]: TemperatureControl,
  [SimulationComponentType.OverpressureTemperature]: OverpressureTemperatureControl,
  [SimulationComponentType.Pcs]: PcsControl,
  [SimulationComponentType.HeatSource]: HeatSourceControl,
  [SimulationComponentType.HvacExchanger]: HvacControl,
};

const { data } = toRefs(useThrsHistory());

const props = defineProps<{ type: ThrsSimulationType }>();

const definition = computed(() => SIMULATION.inputs[props.type] as SimulationDefinitions);

const simulationInputsData = computed(
  () => data.value?.simulation.inputs as unknown as ExtractAllValues<SimulationDefinitions>,
);
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
