<script setup lang="ts">
import { RiArrowDownLine, RiArrowUpLine } from "@remixicon/vue";
import { MimicComponentInstanceProps, useRandomizedNumber } from ".";
import { CircuitBox, CircuitBoxTitle } from "../components/circuit-box";
import {
  ValueList,
  ValueListFlowItem,
  ValueListHeader,
  ValueListSeparator,
  ValueListTemperatureItem,
} from "../components/value-list";

const props = defineProps<MimicComponentInstanceProps & { title: string }>();

const tIn = useRandomizedNumber(40, 90);
const tOut = useRandomizedNumber(40, 90);
const flowIn = useRandomizedNumber(1, 10);
const flowOut = useRandomizedNumber(1, 10);
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
      <ValueListFlowItem :value="flowIn" />
      <ValueListTemperatureItem :in="tIn" />
      <ValueListSeparator />
      <ValueListHeader>
        <RiArrowDownLine class="text-muted-foreground size-3" />
        Out
      </ValueListHeader>
      <ValueListFlowItem :value="flowOut" />
      <ValueListTemperatureItem :out="tOut" />
      <ValueListSeparator />
    </ValueList>
  </CircuitBox>
</template>
