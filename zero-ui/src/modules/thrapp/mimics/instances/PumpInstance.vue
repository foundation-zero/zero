<script setup lang="ts">
import { MimicComponentInstanceProps, useRandomizedState } from ".";
import { PumpState } from "../components/pump";
import Pump from "../components/pump/Pump.vue";

const props = defineProps<MimicComponentInstanceProps>();

const state = useRandomizedState([
  PumpState.Active,
  PumpState.Alarm,
  PumpState.Transient,
  PumpState.Alarm,
]);
</script>

<template>
  <Pump
    v-bind="props"
    :state="state"
  />
</template>
