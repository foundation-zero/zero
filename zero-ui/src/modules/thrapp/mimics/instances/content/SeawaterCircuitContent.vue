<script setup lang="ts">
import { ZiSeawater } from "@/modules/common/components/icons";
import { SensorComponentType } from "@/modules/thrsim/types";
import { MimicComponentInstanceProps } from "..";
import { TooltipComponentContext } from "../../../components/tooltip";
import { MimicComponentType } from "../../../types";
import { CircuitBox, CircuitBoxTitle } from "../../components/circuit-box";
import {
  ValueList,
  ValueListHeatPowerItem,
  ValueListSeparator,
  ValueListTemperatureItem,
} from "../../components/value-list";
import { getMimicDataProvider, ModuleField } from "../../providers";

withDefaults(
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
  <CircuitBox
    v-bind="{ sensors, controllerState, controls, parameters, source, tooltip, custom }"
    :state="state"
  >
    <CircuitBoxTitle class="flex items-center gap-1">
      <ZiSeawater />
      {{ custom.circuitName }}
    </CircuitBoxTitle>

    <ValueList dense>
      <ValueListHeatPowerItem
        v-if="sensors.heatTransfer"
        :source="sensors.heatTransfer as ModuleField<SensorComponentType.HeatTransferDevice>"
      />
      <ValueListSeparator />
      <ValueListTemperatureItem
        :source="source"
        class="text-brand"
        temperature-label="seawater"
      />
      <ValueListSeparator />
    </ValueList>
  </CircuitBox>
</template>
