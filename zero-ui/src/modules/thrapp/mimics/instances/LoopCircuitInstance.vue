<script setup lang="ts">
import AnimatedNumber from "@/modules/loads/components/animated-number/AnimatedNumber.vue";
import { useI18n } from "vue-i18n";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { CircuitBox, CircuitBoxTitle } from "../components/circuit-box";
import {
  ValueList,
  ValueListDeltaTItem,
  ValueListFlowItem,
  ValueListItem,
} from "../components/value-list";
import { getMimicDataProvider } from "../providers";

const { t } = useI18n();
const props = defineProps<
  MimicComponentInstanceProps &
    TooltipComponentContext<MimicComponentType.ExchangeCircuit> & {
      width?: number | string;
      height?: number | string;
      forceHeight?: boolean;
    }
>();

const { getSensorValue, getComponentState } = getMimicDataProvider();

const deltaT = getSensorValue(props.sensors.deltaT);
const tIn = getSensorValue(props.sensors.incoming);
const tOut = getSensorValue(props.sensors.outgoing);
const flow = getSensorValue(props.sensors.flow);
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
        <ValueListDeltaTItem :value="deltaT?.deltaT?.value" />
        <ValueListItem>
          <span class="text-muted-foreground text-2xs">{{ t("units.Tin") }}</span>
          <span class="text-muted-foreground text-xs">
            <AnimatedNumber :to="tIn?.temperature?.value" />{{ t("units.celsius") }}
          </span>
        </ValueListItem>
        <ValueListItem>
          <span class="text-muted-foreground text-2xs">{{ t("units.Tout") }}</span>
          <span class="text-muted-foreground text-xs">
            <AnimatedNumber :to="tOut?.temperature?.value" />{{ t("units.celsius") }}
          </span>
        </ValueListItem>
        <ValueListFlowItem :value="flow?.flow?.value" />
      </ValueList>
    </CircuitBox>
  </MimicTooltipTrigger>
</template>
