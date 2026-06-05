<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrs/types/index.ts";
import { computed } from "vue";
import { MimicComponentInstanceProps } from ".";
import { PumpState } from "../components/pump";
import Pump from "../components/pump/Pump.vue";
import { ModuleField, getMimicDataProvider } from "../providers";

const props = defineProps<
  MimicComponentInstanceProps & { pump: ModuleField<SensorComponentType.Pump> }
>();

const { getSensorValue, getComponentState } = getMimicDataProvider();
const pump = getSensorValue(props.pump);
const state = getComponentState();

const pumpState = computed(() => {
  if (pump.value?.flow.value != undefined && pump.value?.flow.value > 0) return PumpState.Active;
  else return PumpState.Inactive;
});
</script>

<template>
  <Pump
    v-bind="props"
    :pump-state="pumpState"
    :state="state"
  />
</template>
