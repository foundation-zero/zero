<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { RiArrowDownLine, RiArrowLeftLine } from "@remixicon/vue";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { CircuitBox, CircuitBoxTitle } from "../components/circuit-box";
import {
  ValueList,
  ValueListFlowItem,
  ValueListHeader,
  ValueListSeparator,
  ValueListTemperatureItem,
} from "../components/value-list";
import { getMimicDataProvider } from "../providers";

const props = defineProps<
  MimicComponentInstanceProps &
    TooltipComponentContext<MimicComponentType.HotWaterCircuit> & {
      width?: number | string;
      height?: number | string;
      forceHeight?: boolean;
    }
>();

const { getComponentState } = getMimicDataProvider();
const state = getComponentState();

const t = tScoped("labels");
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.HotWaterCircuit"
    :data="props"
  >
    <CircuitBox
      v-bind="props"
      :state="state"
    >
      <CircuitBoxTitle>{{ tooltip?.title }}</CircuitBoxTitle>
      <ValueList>
        <ValueListSeparator />
        <ValueListHeader>
          <RiArrowDownLine class="text-muted-foreground size-3" />
          {{ t("from") }}
        </ValueListHeader>
        <ValueListFlowItem :source="sensors.flowIn" />
        <ValueListTemperatureItem :source="sensors.tIn" />
        <ValueListSeparator />
        <ValueListHeader>
          <RiArrowLeftLine class="text-muted-foreground size-3" />
          {{ t("to") }}
        </ValueListHeader>
        <ValueListFlowItem :source="sensors.flowOut" />
        <ValueListTemperatureItem :source="sensors.tOut" />
        <ValueListSeparator />
      </ValueList>
    </CircuitBox>
    <slot />
  </MimicTooltipTrigger>
</template>
