<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrs/types";
import { computed } from "vue";
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
      width?: number | string;
      height?: number | string;
      forceHeight?: boolean;
      level: ModuleField<SensorComponentType.Level>;
      temperature: ModuleField<SensorComponentType.Temperature>;
    }
>();

const { getSensorValue } = getMimicDataProvider();

const level = getSensorValue(props.level);
const fillLevel = computed(() => (level.value?.level.value ?? 0) / 2.75);
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
    v-bind="props"
    :level="fillLevel"
    :mode="mode"
  >
    <YardTag>{{ tagId }}</YardTag>
    <BoilerTankTitle>{{ title }}</BoilerTankTitle>
    <BoilerTankMode :mode="mode" />
    <ValueList class="gap-0">
      <ValueListTemperatureItem :temperature="temperature?.temperature.value" />
      <ValueListFillLevelItem :value="fillLevel" />
      <ValueListTimeItem
        v-if="mode === BoilerTankModes.Boosting"
        :value="fillTime"
      />
    </ValueList>
  </BoilerTank>
</template>
