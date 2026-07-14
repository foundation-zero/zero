<script setup lang="ts">
import { RiSnowflakeLine } from "@remixicon/vue";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { HeatPump, HeatPumpTitle } from "../components/heat-pump";
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
    TooltipComponentContext<MimicComponentType.HVAC> & {
      width?: number | string;
      height?: number | string;
      forceHeight?: boolean;
    }
>();

const { getSensorValue, getComponentState } = getMimicDataProvider();

const heatExchanger = getSensorValue(props.source);
const state = getComponentState();
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.HVAC"
    :data="props"
  >
    <HeatPump
      v-bind="props"
      :state="state"
    >
      <YardTag>{{ tooltip?.yardTag }}</YardTag>
      <HeatPumpTitle class="gap-1 py-1">
        <RiSnowflakeLine class="text-brand inline h-4 w-4" />
        {{ tooltip?.title }}
      </HeatPumpTitle>
      <ValueList class="gap-0">
        <ValueListSeparator />
        <ValueListHeatPowerItem :value="heatExchanger?.heat?.value" />
        <ValueListDeltaTItem :value="heatExchanger?.deltaT.value" />
        <ValueListSeparator />
      </ValueList>
    </HeatPump>
    <slot />
  </MimicTooltipTrigger>
</template>
