<script setup lang="ts">
import { ZiSeawater } from "@/modules/common/components/icons";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { CircuitBox, CircuitBoxTitle } from "../components/circuit-box";
import { ValueList, ValueListSeparator, ValueListTemperatureItem } from "../components/value-list";
import { getMimicDataProvider } from "../providers";

const props = withDefaults(
  defineProps<
    MimicComponentInstanceProps &
      TooltipComponentContext<MimicComponentType.SeawaterCircuit> & {
        width?: number | string;
        height?: number | string;
        forceHeight?: boolean;
      }
  >(),
  { height: 90 },
);

const { getComponentState } = getMimicDataProvider();

const state = getComponentState();
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.SeawaterCircuit"
    :data="props"
  >
    <CircuitBox
      v-bind="props"
      :state="state"
    >
      <CircuitBoxTitle class="flex items-center gap-1"><ZiSeawater />Seawater</CircuitBoxTitle>

      <ValueList dense>
        <ValueListSeparator />
        <ValueListTemperatureItem
          :source="source"
          class="text-brand"
          temperature-label="seawater"
        />
        <ValueListSeparator />
      </ValueList>
    </CircuitBox>
    <slot />
  </MimicTooltipTrigger>
</template>
