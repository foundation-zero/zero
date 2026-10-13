<script setup lang="ts">
import { RiTempHotLine } from "@remixicon/vue";
import { computed } from "vue";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { AssetBox, AssetBoxTitle } from "../components/asset-box";
import { HeatPumpMode, HeatPumpModes } from "../components/heat-pump";
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
    TooltipComponentContext<MimicComponentType.HeatPump> & {
      width?: number | string;
      height?: number | string;
      forceHeight?: boolean;
    }
>();
const { getComponentState, getControlValue } = getMimicDataProvider();

const heatpump = getControlValue(props.controls.heatpump);
const state = getComponentState();

const mode = computed(() => {
  if (heatpump.value?.on.value) return HeatPumpModes.Active;
  else return HeatPumpModes.Inactive;
});
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.HeatPump"
    :data="props"
  >
    <AssetBox
      v-bind="props"
      :state="state"
    >
      <YardTag>{{ tooltip?.yardTag }}</YardTag>
      <AssetBoxTitle class="gap-1 py-1">
        <RiTempHotLine class="text-brand inline h-4 w-4" />
        {{ tooltip?.title }}
      </AssetBoxTitle>
      <HeatPumpMode
        :mode="mode"
        :state="state"
      />
      <ValueList
        dense
        class="pt-1"
      >
        <ValueListSeparator />
        <ValueListHeatPowerItem :source="sensors.heatTransfer" />
        <ValueListDeltaTItem :source="sensors.heatTransfer" />
        <ValueListSeparator />
      </ValueList>
    </AssetBox>
  </MimicTooltipTrigger>
</template>
