<script setup lang="ts">
import { MimicComponentInstanceProps, useRandomizedNumber, useRandomizedState } from ".";
import {
  BoilerTank,
  BoilerTankMode,
  BoilerTankModes,
  BoilerTankTitle,
} from "../components/boiler-tank";
import {
  ValueList,
  ValueListFillLevelItem,
  ValueListTemperatureItem,
  ValueListTimeItem,
} from "../components/value-list";
import YardTag from "../components/yard-tag/YardTag.vue";

const props = defineProps<MimicComponentInstanceProps & { title: string }>();

const tIn = useRandomizedNumber(40, 90);
const tOut = useRandomizedNumber(40, 90);
const fillLevel = useRandomizedNumber(0, 100);
const fillTime = useRandomizedNumber(0, 60);
const mode = useRandomizedState([
  BoilerTankModes.InUse,
  BoilerTankModes.Boosting,
  BoilerTankModes.Standby,
]);
</script>

<template>
  <BoilerTank
    :level="fillLevel"
    v-bind="props"
    :mode="mode"
  >
    <YardTag>{{ tagId }}</YardTag>
    <BoilerTankTitle>{{ title }}</BoilerTankTitle>
    <BoilerTankMode :mode="mode" />
    <ValueList class="gap-0">
      <ValueListTemperatureItem
        :in="tIn"
        :out="tOut"
      />
      <ValueListFillLevelItem :value="fillLevel" />
      <ValueListTimeItem
        v-if="mode === BoilerTankModes.Boosting"
        :value="fillTime"
      />
    </ValueList>
  </BoilerTank>
</template>
