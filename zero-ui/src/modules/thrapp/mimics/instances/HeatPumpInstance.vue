<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrs/types";
import { computed, type Component } from "vue";
import { MimicComponentInstanceProps, TitleProps } from ".";
import { HeatPump, HeatPumpMode, HeatPumpModes, HeatPumpTitle } from "../components/heat-pump";
import {
  ValueList,
  ValueListDeltaTItem,
  ValueListHeatPowerItem,
  ValueListSeparator,
} from "../components/value-list";
import { YardTag } from "../components/yard-tag";
import { getMimicDataProvider, ModuleField } from "../providers";

const props = defineProps<
  MimicComponentInstanceProps &
    TitleProps & {
      heatExchanger: ModuleField<SensorComponentType.HeatExchanger>;
    } & {
      icon: Component;
      width?: number | string;
      height?: number | string;
      forceHeight?: boolean;
      hideMode?: boolean;
    }
>();

const { getSensorValue } = getMimicDataProvider();

const heatExchanger = getSensorValue(props.heatExchanger);

const mode = computed(() => {
  if (heatExchanger.value?.heat.value !== 0) return HeatPumpModes.Active;
  else return HeatPumpModes.Inactive;
});
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
    <HeatPumpMode
      v-if="!hideMode"
      :mode="mode"
    />
    <ValueList class="gap-0">
      <ValueListSeparator />
      <ValueListHeatPowerItem :value="heatExchanger?.heat?.value" />
      <ValueListDeltaTItem :value="heatExchanger?.deltaT.value" />
      <ValueListSeparator />
    </ValueList>
  </HeatPump>
</template>
