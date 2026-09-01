<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { RiArrowDownLine } from "@remixicon/vue";
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
    TooltipComponentContext<MimicComponentType.ConnectingCircuit> & {
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
    :type="MimicComponentType.ConnectingCircuit"
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
          <slot name="from">
            <RiArrowDownLine class="text-muted-foreground size-3" />
            {{ t("from") }}
          </slot>
        </ValueListHeader>
        <ValueListFlowItem :source="sensors.flowIn" />
        <ValueListTemperatureItem :source="sensors.tIn" />
        <ValueListSeparator />
        <ValueListHeader>
          <slot name="to">
            <RiArrowDownLine class="text-muted-foreground size-3" />
            {{ t("to") }}
          </slot>
        </ValueListHeader>
        <ValueListFlowItem :source="sensors.flowOut" />
        <ValueListTemperatureItem :source="sensors.tOut" />
        <ValueListSeparator />
      </ValueList>
    </CircuitBox>
    <slot />
  </MimicTooltipTrigger>
</template>
