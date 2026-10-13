<script setup lang="ts">
import { RiSnowflakeLine } from "@remixicon/vue";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { AssetBox, AssetBoxTitle } from "../components/asset-box";
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

const { getComponentState } = getMimicDataProvider();

const state = getComponentState();
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.HVAC"
    :data="props"
  >
    <AssetBox
      v-bind="props"
      :state="state"
    >
      <YardTag>{{ tooltip?.yardTag }}</YardTag>
      <AssetBoxTitle class="gap-1 py-1">
        <RiSnowflakeLine class="text-brand inline h-4 w-4" />
        {{ tooltip?.title }}
      </AssetBoxTitle>
      <ValueList dense>
        <ValueListSeparator />
        <ValueListHeatPowerItem :source="source" />
        <ValueListDeltaTItem :source="source" />
        <ValueListSeparator />
      </ValueList>
    </AssetBox>
  </MimicTooltipTrigger>
</template>
