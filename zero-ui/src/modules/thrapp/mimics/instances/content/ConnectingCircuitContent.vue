<script setup lang="ts">
import { RiArrowDownLine, RiArrowUpLine } from "@remixicon/vue";
import { MimicComponentInstanceProps } from "..";
import { TooltipComponentContext } from "../../../components/tooltip";
import { MimicComponentType } from "../../../types";
import { CircuitBox, CircuitBoxTitle } from "../../components/circuit-box";
import { ModeBadges, ModeBadgeSize } from "../../components/mode-badge";
import {
  ValueList,
  ValueListDeltaTItem,
  ValueListFlowItem,
  ValueListHeatPowerItem,
  ValueListSeparator,
  ValueListTemperatureItem,
} from "../../components/value-list";
import { getMimicDataProvider } from "../../providers";

defineProps<
  MimicComponentInstanceProps &
    TooltipComponentContext<MimicComponentType.ConnectingCircuit> & { inverted?: boolean }
>();

const { getComponentState } = getMimicDataProvider();
const state = getComponentState();
</script>

<template>
  <CircuitBox :state="state">
    <CircuitBoxTitle class="gap-1 py-1">
      <span class="flex max-w-full flex-nowrap">
        <RiArrowUpLine class="text-muted-foreground size-3" />
        <RiArrowDownLine class="text-muted-foreground size-3" />
      </span>
      {{ custom.circuitName }}
    </CircuitBoxTitle>

    <ModeBadges
      :module="custom.modeModule"
      :size="ModeBadgeSize.Circuit"
    />

    <ValueList
      dense
      class="pt-1"
    >
      <ValueListHeatPowerItem :source="source" />
      <ValueListSeparator />
      <ValueListDeltaTItem :source="source" />
      <ValueListTemperatureItem
        class="text-xs"
        :source="source"
        :field="!inverted ? 'temperatureSupply' : 'temperatureReturn'"
        temperature-label="in"
      />
      <ValueListTemperatureItem
        class="text-xs"
        :source="source"
        :field="!inverted ? 'temperatureReturn' : 'temperatureSupply'"
        temperature-label="out"
      />
      <ValueListFlowItem :source="source" />
      <ValueListSeparator />
    </ValueList>
  </CircuitBox>
</template>
