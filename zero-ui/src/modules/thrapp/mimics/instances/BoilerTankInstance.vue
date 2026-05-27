<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrs/types";
import {
  MimicComponentInstanceProps,
  ModuleProp,
  TitleProps,
  useRandomizedNumber,
  useRandomizedState,
} from ".";
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
import { getMimicDataProvider } from "../providers";

const props = defineProps<
  MimicComponentInstanceProps &
    TitleProps & {
      level: ModuleProp<SensorComponentType.Level>;
      temperature: ModuleProp<SensorComponentType.Temperature>;
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
    :level="fillLevel?.level.value ?? 0"
    :mode="mode"
  >
    <YardTag>{{ tagId }}</YardTag>
    <BoilerTankTitle>{{ title }}</BoilerTankTitle>
    <BoilerTankMode :mode="mode" />
    <ValueList class="gap-0">
      <ValueListTemperatureItem :in="temperature?.temperature.value ?? 0" />
      <ValueListFillLevelItem :value="fillLevel?.level.value" />
      <ValueListTimeItem
        v-if="mode === BoilerTankModes.Boosting"
        :value="fillTime"
      />
    </ValueList>
  </BoilerTank>
</template>
