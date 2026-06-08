<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrs/types";
import { RiArrowDownLine, RiArrowUpLine } from "@remixicon/vue";
import { MimicComponentInstanceProps, TitleProps } from ".";
import { CircuitBox, CircuitBoxTitle } from "../components/circuit-box";
import {
  ValueList,
  ValueListFlowItem,
  ValueListHeader,
  ValueListSeparator,
  ValueListTemperatureItem,
} from "../components/value-list";
import { getMimicDataProvider, ModuleField } from "../providers";

const props = defineProps<
  MimicComponentInstanceProps &
    TitleProps & {
      width?: number | string;
      height?: number | string;
      forceHeight?: boolean;
      flowIn: ModuleField<SensorComponentType.CalculatedFlow>;
      tIn: ModuleField<SensorComponentType.Temperature>;
      flowOut: ModuleField<SensorComponentType.Flow>;
      tOut: ModuleField<SensorComponentType.Temperature>;
    }
>();

const { getSensorValue, getComponentState } = getMimicDataProvider();
const flowIn = getSensorValue(props.flowIn);
const tIn = getSensorValue(props.tIn);
const flowOut = getSensorValue(props.flowOut);
const tOut = getSensorValue(props.tOut);
const state = getComponentState();
</script>

<template>
  <CircuitBox
    v-bind="props"
    :state="state"
  >
    <CircuitBoxTitle>{{ title }}</CircuitBoxTitle>
    <ValueList>
      <ValueListSeparator />
      <ValueListHeader>
        <RiArrowUpLine class="text-muted-foreground size-3" />
        In
      </ValueListHeader>
      <ValueListFlowItem :value="flowIn?.flow.value" />
      <ValueListTemperatureItem :temperature="tIn?.temperature.value" />
      <ValueListSeparator />
      <ValueListHeader>
        <RiArrowDownLine class="text-muted-foreground size-3" />
        Out
      </ValueListHeader>
      <ValueListFlowItem :value="flowOut?.flow.value" />
      <ValueListTemperatureItem :temperature="tOut?.temperature.value" />
      <ValueListSeparator />
    </ValueList>
  </CircuitBox>
</template>
