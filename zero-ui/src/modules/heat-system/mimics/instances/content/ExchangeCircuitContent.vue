<script setup lang="ts">
import { MimicComponentInstanceProps } from "..";
import { TooltipComponentContext } from "../../../components/tooltip";
import { MimicComponentType } from "../../../types";
import { CircuitBox, CircuitBoxTitle } from "../../components/circuit-box";
import { ModeBadges, ModeBadgeSize } from "../../components/mode-badge";
import {
  ValueList,
  ValueListDeltaTItem,
  ValueListFlowItem,
  ValueListSeparator,
  ValueListTemperatureItem,
} from "../../components/value-list";
import { getMimicDataProvider } from "../../providers";

defineProps<
  MimicComponentInstanceProps &
    TooltipComponentContext<MimicComponentType.ExchangeCircuit> & {
      width?: number | string;
      height?: number | string;
      forceHeight?: boolean;
    }
>();

const { getComponentState } = getMimicDataProvider();

const state = getComponentState();
</script>

<template>
  <CircuitBox :state="state">
    <CircuitBoxTitle class="mb-1">
      {{ custom.circuitName }}
    </CircuitBoxTitle>

    <ModeBadges
      :module="custom.modeModule"
      :size="ModeBadgeSize.Circuit"
    />

    <ValueList dense>
      <ValueListSeparator />
      <ValueListDeltaTItem :source="source" />
      <ValueListTemperatureItem
        class="text-xs"
        :source="source"
        field="temperatureSupply"
        temperature-label="in"
      />
      <ValueListTemperatureItem
        class="text-xs"
        :source="source"
        field="temperatureReturn"
        temperature-label="out"
      />
      <ValueListFlowItem :source="source" />
      <ValueListSeparator />
    </ValueList>
  </CircuitBox>
</template>
