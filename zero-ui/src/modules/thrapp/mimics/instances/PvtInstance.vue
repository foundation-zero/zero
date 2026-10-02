<script setup lang="ts">
import { ZiSolarPanel } from "@/modules/common/components/icons";
import { usePvtMode } from "@/modules/thrapp/state";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { Pvt, PvtMode, PvtTitle } from "../components/pvt";
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
    height: 228,
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
    <Pvt
      v-bind="props"
      :state="state"
      :height="180"
    >
      <YardTag>{{ props.tagId }}</YardTag>
      <PvtTitle class="gap-2 pb-1">
        <ZiSolarPanel class="fill-brand-muted" />
        {{ props.tooltip?.title }}
      </PvtTitle>

      <PvtMode
        :mode="modeKey"
        :state="state"
      />
      <ValueList
        dense
        class="gap-0 pt-1"
      >
        <ValueListSeparator />

        <ValueListHeatPowerItem :source="props.sensors.heatTransfer" />
        <ValueListDeltaTItem :source="props.sensors.heatTransfer" />
        <ValueListFlowItem :source="props.sensors.heatTransfer" />
        <ValueListPowerItem :source="props.source" />

        <ValueListSeparator />
      </ValueList>
    </Pvt>
  </MimicTooltipTrigger>
</template>
