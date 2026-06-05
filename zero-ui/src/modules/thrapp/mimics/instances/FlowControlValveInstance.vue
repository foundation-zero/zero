<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrs/types/index.ts";
import ActuatedValve from "../components/actuated-valve/ActuatedValve.vue";
import MixValve from "../components/actuated-valve/MixValve.vue";
import TwoWayValve from "../components/actuated-valve/TwoWayValve.vue";
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
    <TwoWayValve :flow="valve?.positionRel.value ?? 0" />
    <MixValve />
  </ActuatedValve>
</template>
