<script setup lang="ts">
import { MimicComponentInstanceProps, useRandomizedState } from ".";
import {
  ActuatedValveType,
  FlowValveState,
  SwitchValveState,
  ThreeWayValveState,
} from "../components/actuated-valve";
import ActuatedValve from "../components/actuated-valve/ActuatedValve.vue";

const props = defineProps<MimicComponentInstanceProps & { type: ActuatedValveType }>();

const valveStates = {
  [ActuatedValveType.Switch]: [SwitchValveState.Open, SwitchValveState.Closed],
  [ActuatedValveType.FlowControl]: [
    FlowValveState.Open,
    FlowValveState.Closed,
    FlowValveState.Partial,
  ],
  [ActuatedValveType.ThreeWay]: [
    ThreeWayValveState.Open,
    ThreeWayValveState.Closed,
    ThreeWayValveState.AA,
    ThreeWayValveState.AB,
    ThreeWayValveState.BA,
  ],
};

const state = useRandomizedState<SwitchValveState | FlowValveState | ThreeWayValveState>(
  valveStates[props.type],
);
</script>

<template>
  <ActuatedValve
    v-bind="props"
    :state="state"
  />
</template>
