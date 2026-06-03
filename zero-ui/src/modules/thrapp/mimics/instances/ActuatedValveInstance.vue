<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrs/types/index.ts";
import { computed } from "vue";
import { MimicComponentInstanceProps } from ".";
import { ActuatedValveType, SwitchValveState } from "../components/actuated-valve";
import ActuatedValve from "../components/actuated-valve/ActuatedValve.vue";
import { getMimicDataProvider, ModuleField } from "../providers";

const props = defineProps<
  MimicComponentInstanceProps & {
    type: ActuatedValveType;
    valve: ModuleField<SensorComponentType.Valve>;
  }
>();

const { getSensorValue } = getMimicDataProvider();
const valve = getSensorValue(props.valve);

const CLOSED_THRESHOLD = 0.0001;

const state = computed(() => {
  if (
    valve.value?.positionRel.value != undefined &&
    valve.value?.positionRel.value <= CLOSED_THRESHOLD
  )
    return SwitchValveState.Closed;
  else return SwitchValveState.Open;
});
</script>

<template>
  <ActuatedValve
    v-bind="props"
    :state="state"
  />
</template>
