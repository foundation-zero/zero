<script setup lang="ts">
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { CircuitBox, CircuitBoxTitle } from "../components/circuit-box";
import { ModeBadges, ModeBadgeSize } from "../components/mode-badge";
import {
  ValueList,
  ValueListDeltaTItem,
  ValueListFlowItem,
  ValueListTemperatureItem,
} from "../components/value-list";
import { getMimicDataProvider } from "../providers";

const props = defineProps<
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
  <MimicTooltipTrigger
    :type="MimicComponentType.ExchangeCircuit"
    :data="props"
  >
    <CircuitBox
      v-bind="props"
      :state="state"
    >
      <CircuitBoxTitle>{{ custom.circuitName }}</CircuitBoxTitle>

      <ModeBadges
        :module="custom.modeModule"
        :size="ModeBadgeSize.Circuit"
      />

      <ValueList>
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
      </ValueList>
    </CircuitBox>
    <slot />
  </MimicTooltipTrigger>
</template>
