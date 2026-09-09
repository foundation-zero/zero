<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrsim/types";
import { useI18n } from "vue-i18n";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { CircuitBox, CircuitBoxTitle } from "../components/circuit-box";
import {
  ValueList,
  ValueListDeltaTItem,
  ValueListFlowItem,
  ValueListTemperatureItem,
} from "../components/value-list";
import { getMimicDataProvider, ModuleField } from "../providers";

const { t } = useI18n();
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
      <CircuitBoxTitle>{{ tooltip?.title }}</CircuitBoxTitle>
      <ValueList>
        <ValueListDeltaTItem
          v-if="sensors.deltaT?.[0]"
          :source="sensors.deltaT as ModuleField<SensorComponentType.DeltaT>"
        />
        <ValueListTemperatureItem
          class="text-xs"
          :source="sensors.incoming"
        >
          {{ t("units.Tin") }}
        </ValueListTemperatureItem>
        <ValueListTemperatureItem
          class="text-xs"
          :source="sensors.outgoing"
        >
          {{ t("units.Tout") }}
        </ValueListTemperatureItem>
        <ValueListFlowItem :source="sensors.flow" />
      </ValueList>
    </CircuitBox>
    <slot />
  </MimicTooltipTrigger>
</template>
