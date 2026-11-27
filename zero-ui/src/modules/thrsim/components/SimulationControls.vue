<script setup lang="ts">
import { SIMULATION, ThrsSimulationType } from "@/modules/thrsim/lib/consts.ts";
import {
  ExtractAllValues,
  SimulationComponentType,
  SimulationDefinitions,
} from "@/modules/thrsim/types";
import { type Component, computed, toRefs } from "vue";
import { useSimulationStore } from "../stores/simulation";
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
  [SimulationComponentType.ActiveHeatSource]: HeatSourceControl,
  [SimulationComponentType.HvacExchanger]: HvacControl,
  [SimulationComponentType.AmcsMode]: null,
  [SimulationComponentType.AdsorptionChiller]: null,
  [SimulationComponentType.Ugrid]: HeatSourceControl,
  [SimulationComponentType.PropulsionDrive]: HeatSourceControl,
};

const { simulation } = toRefs(useSimulationStore());

const props = defineProps<{ type: ThrsSimulationType }>();

const definition = computed(() => SIMULATION.inputs[props.type] as SimulationDefinitions);

const simulationInputsData = computed(
  () => simulation.value?.inputs as unknown as ExtractAllValues<SimulationDefinitions>,
);
</script>
<template>
  <ModuleControls
    v-if="definition && simulationInputsData"
    :controls="definition"
    :data="simulationInputsData"
    :disabled="false"
  >
    <template #default="{ componentName, componentDefinition, values }">
      <component
        :is="COMPONENTS[componentDefinition.componentType]"
        :values="values"
        :component-name="componentName"
        :component-type="componentDefinition.componentType"
      />
    </template>
  </ModuleControls>
</template>
