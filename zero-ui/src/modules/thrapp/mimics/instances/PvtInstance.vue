<script setup lang="ts">
import { ZiSolarPanel } from "@/modules/common/components/icons";
import { usePvtMode } from "@/modules/thrapp/state";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { AssetBox, AssetBoxTitle } from "../components/asset-box";
import { PvtMode } from "../components/pvt";
import {
  ValueList,
  ValueListDeltaTItem,
  ValueListFlowItem,
  ValueListHeatPowerItem,
  ValueListPowerItem,
  ValueListSeparator,
} from "../components/value-list";
import { YardTag } from "../components/yard-tag";
import { getMimicDataProvider } from "../providers";

const props = withDefaults(
  defineProps<
    MimicComponentInstanceProps &
      TooltipComponentContext<MimicComponentType.Pvt> & {
        width?: number | string;
        height?: number | string;
        forceHeight?: boolean;
      }
  >(),
  {
    width: 220,
    height: 200,
    forceHeight: true,
  },
);

const { getComponentState } = getMimicDataProvider();

const state = getComponentState();

const modeKey = usePvtMode(props.custom.group);
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.Pvt"
    :data="props"
  >
    <AssetBox
      v-bind="props"
      :state="state"
    >
      <YardTag>{{ tooltip?.yardTag }}</YardTag>
      <AssetBoxTitle class="pb-1">
        <ZiSolarPanel class="fill-brand-muted" />
        {{ tooltip?.title }}
      </AssetBoxTitle>

      <PvtMode
        :mode="modeKey"
        :state="state"
      />

      <ValueList dense>
        <ValueListSeparator />

        <ValueListHeatPowerItem :source="sensors.heatTransfer" />
        <ValueListDeltaTItem :source="sensors.heatTransfer" />
        <ValueListFlowItem :source="sensors.heatTransfer" />
        <ValueListPowerItem :source="source" />

        <ValueListSeparator />
      </ValueList>
    </AssetBox>
  </MimicTooltipTrigger>
</template>
