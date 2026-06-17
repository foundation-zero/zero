<script setup lang="ts">
import { computed } from "vue";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { HeatPump, HeatPumpMode, HeatPumpModes, HeatPumpTitle } from "../components/heat-pump";
import {
  ValueList,
  ValueListDeltaTItem,
  ValueListHeatPowerItem,
  ValueListSeparator,
} from "../components/value-list";
import { YardTag } from "../components/yard-tag";
import { getMimicDataProvider } from "../providers";

const props = defineProps<
  MimicComponentInstanceProps &
    TooltipComponentContext<MimicComponentType.Asset> & {
      width?: number | string;
      height?: number | string;
      forceHeight?: boolean;
    }
>();

const { getSensorValue, getComponentState } = getMimicDataProvider();

const heatExchanger = getSensorValue(props.sensors.heatExchanger);
const state = getComponentState();

const mode = computed(() => {
  if (heatExchanger.value?.heat.value !== 0) return HeatPumpModes.Active;
  else return HeatPumpModes.Inactive;
});
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.Asset"
    :data="props"
  >
    <HeatPump
      v-bind="props"
      :state="state"
    >
      <YardTag>{{ tooltip?.yardTag }}</YardTag>
      <HeatPumpTitle class="gap-1 py-1">
        <component
          :is="custom.icon"
          class="text-brand inline h-4 w-4"
        />
        {{ tooltip?.title }}
      </HeatPumpTitle>
      <HeatPumpMode
        v-if="!custom.hideMode"
        :mode="mode"
        :state="state"
      />
      <ValueList class="gap-0">
        <ValueListSeparator />
        <ValueListHeatPowerItem :value="heatExchanger?.heat?.value" />
        <ValueListDeltaTItem :value="heatExchanger?.deltaT.value" />
        <ValueListSeparator />
      </ValueList>
    </HeatPump>
  </MimicTooltipTrigger>
</template>
