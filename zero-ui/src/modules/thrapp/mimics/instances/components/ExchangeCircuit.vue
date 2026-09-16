<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrsim/types";
import { useI18n } from "vue-i18n";
import { MimicComponentInstanceProps } from "..";
import { TooltipComponentContext } from "../../../components/tooltip";
import { MimicComponentType } from "../../../types";
import { CircuitBox, CircuitBoxTitle } from "../../components/circuit-box";
import { ModeBadges, ModeBadgeSize } from "../../components/mode-badge";
import {
  ValueList,
  ValueListDeltaTItem,
  ValueListFlowItem,
  ValueListSeparator,
  ValueListTemperatureItem,
} from "../../components/value-list";
import { getMimicDataProvider, ModuleField } from "../../providers";

const { t } = useI18n();
defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.ExchangeCircuit>
>();

const { getComponentState } = getMimicDataProvider();

const state = getComponentState();
</script>

<template>
  <CircuitBox :state="state">
    <CircuitBoxTitle class="mb-1">
      <slot>
        {{ tooltip?.title }}
      </slot>
    </CircuitBoxTitle>
    <slot name="content">
      <ModeBadges
        :module="custom.modeModule"
        :size="ModeBadgeSize.Circuit"
      />
      <ValueList class="mt-1">
        <ValueListSeparator />
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
        <ValueListSeparator />
      </ValueList>
    </slot>
  </CircuitBox>
</template>
