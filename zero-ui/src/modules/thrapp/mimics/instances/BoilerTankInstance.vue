<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrs/types";
import { MimicComponentInstanceProps, TitleProps } from ".";
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
import { getMimicDataProvider, ModuleField } from "../providers";
import { useRandomizedNumber, useRandomizedState } from "../providers/mock-helpers.ts";

const props = defineProps<
  MimicComponentInstanceProps &
    TitleProps & {
      level: ModuleField<SensorComponentType.Level>;
      temperature: ModuleField<SensorComponentType.Temperature>;
    }
>();

const { getSensorValue } = getMimicDataProvider();

const fillLevel = getSensorValue(props.level);
const temperature = getSensorValue(props.temperature);

const fillTime = useRandomizedNumber(0, 60);
const mode = useRandomizedState([
  BoilerTankModes.InUse,
  BoilerTankModes.Boosting,
  BoilerTankModes.Standby,
]);
</script>

<template>
  <BoilerTank
    :x="x"
    :y="y"
    :level="fillLevel?.level.value ?? 0"
    :mode="mode"
  >
    <YardTag>{{ tagId }}</YardTag>
    <BoilerTankTitle>{{ title }}</BoilerTankTitle>
    <BoilerTankMode :mode="mode" />
    <ValueList class="gap-0">
      <ValueListTemperatureItem :temperature="temperature?.temperature.value" />
      <ValueListFillLevelItem :value="fillLevel?.level.value" />
      <ValueListTimeItem
        v-if="mode === BoilerTankModes.Boosting"
        :value="fillTime"
      />
    </ValueList>
  </BoilerTank>
</template>
