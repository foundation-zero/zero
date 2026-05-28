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
      flowIn: ModuleField<SensorComponentType.Flow>;
      flowOut: ModuleField<SensorComponentType.Flow>;
    }
>();

const { getSensorValue } = getMimicDataProvider();
const flowIn = getSensorValue(props.flowIn);
const flowOut = getSensorValue(props.flowOut);
</script>

<template>
  <CircuitBox v-bind="props">
    <CircuitBoxTitle>{{ title }}</CircuitBoxTitle>
    <ValueList>
      <ValueListSeparator />
      <ValueListHeader>
        <RiArrowUpLine class="text-muted-foreground size-3" />
        In
      </ValueListHeader>
      <ValueListFlowItem :value="flowIn?.flow.value" />
      <ValueListTemperatureItem :temperature="flowIn?.temperature.value" />
      <ValueListSeparator />
      <ValueListHeader>
        <RiArrowDownLine class="text-muted-foreground size-3" />
        Out
      </ValueListHeader>
      <ValueListFlowItem :value="flowOut?.flow.value" />
      <ValueListTemperatureItem :temperature="flowOut?.temperature.value" />
      <ValueListSeparator />
    </ValueList>
  </CircuitBox>
</template>
