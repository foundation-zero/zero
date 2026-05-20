<script setup lang="ts">
import { type Component } from "vue";
import { MimicComponentInstanceProps, useRandomizedNumber, useRandomizedState } from ".";
import { HeatPump, HeatPumpMode, HeatPumpModes, HeatPumpTitle } from "../components/heat-pump";
import {
  ValueList,
  ValueListDeltaTItem,
  ValueListHeatPowerItem,
  ValueListSeparator,
} from "../components/value-list";
import { YardTag } from "../components/yard-tag";

const props = defineProps<
  MimicComponentInstanceProps & {
    icon: Component;
    title: string;
    width: number | string;
    height: number | string;
  }
>();

const deltaT = useRandomizedNumber(-20, 20);
const heatPower = useRandomizedNumber(5, 30);
const mode = useRandomizedState([HeatPumpModes.Active, HeatPumpModes.Inactive]);
</script>

<template>
  <HeatPump v-bind="props">
    <YardTag>{{ tagId }}</YardTag>
    <HeatPumpTitle class="gap-1 py-1">
      <component
        :is="icon"
        class="text-brand inline h-4 w-4"
      />
      {{ title }}
    </HeatPumpTitle>
    <HeatPumpMode :mode="mode" />
    <ValueList class="gap-0">
      <ValueListSeparator />
      <ValueListHeatPowerItem :value="heatPower" />
      <ValueListDeltaTItem :value="deltaT" />
      <ValueListSeparator />
    </ValueList>
  </HeatPump>
</template>
