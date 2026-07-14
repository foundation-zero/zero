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

const { getSensorValue, getComponentState } = getMimicDataProvider();
const flowIn = getSensorValue(props.sensors.flowIn);
const tIn = getSensorValue(props.sensors.tIn);
const flowOut = getSensorValue(props.sensors.flowOut);
const tOut = getSensorValue(props.sensors.tOut);
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
        <ValueListFlowItem :value="flowIn?.flow.value" />
        <ValueListTemperatureItem :temperature="tIn?.temperature.value" />
        <ValueListSeparator />
        <ValueListHeader>
          <RiArrowLeftLine class="text-muted-foreground size-3" />
          {{ t("to") }}
        </ValueListHeader>
        <ValueListFlowItem :value="flowOut?.flow.value" />
        <ValueListTemperatureItem :temperature="tOut?.temperature.value" />

        <ValueListSeparator />
      </ValueList>
    </CircuitBox>
    <slot />
  </MimicTooltipTrigger>
</template>
