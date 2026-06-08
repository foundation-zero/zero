<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrs/types/index.ts";
import ActuatedValve from "../components/actuated-valve/ActuatedValve.vue";
import SwitchValve from "../components/actuated-valve/SwitchValve.vue";
import ThreeWayValve from "../components/actuated-valve/ThreeWayValve.vue";
import { getMimicDataProvider, ModuleField } from "../providers/index.ts";
import { MimicComponentInstanceProps } from "./index.ts";

const props = defineProps<
  MimicComponentInstanceProps & {
    valve: ModuleField<SensorComponentType.Valve>;
  }
>();

const { getSensorValue, getComponentState } = getMimicDataProvider();
const valve = getSensorValue(props.valve);
const state = getComponentState();
</script>

<template>
  <ActuatedValve
    v-bind="props"
    :state="state"
  >
    <SwitchValve />
    <ThreeWayValve :flow="valve?.positionRel.value ?? 0" />
  </ActuatedValve>
</template>
