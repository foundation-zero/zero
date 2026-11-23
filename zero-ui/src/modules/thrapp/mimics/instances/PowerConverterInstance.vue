<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { reactiveOmit } from "@vueuse/core";
import { useI18n } from "vue-i18n";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { AssetBox, AssetBoxTitle } from "../components/asset-box";
import {
  POWER_CONVERTER_HEIGHT,
  POWER_CONVERTER_ICONS,
  POWER_CONVERTER_TITLES,
  POWER_CONVERTER_WIDTH,
} from "../components/power-converter";
import {
  ValueList,
  ValueListDeltaTItem,
  ValueListHeatPowerItem,
  ValueListPowerItem,
  ValueListSeparator,
  ValueListTemperatureItem,
} from "../components/value-list";
import { YardTag } from "../components/yard-tag";
import { getMimicDataProvider, ModuleField, SensorValue } from "../providers";
import { FieldRenderer } from "../renderers";

const props = withDefaults(
  defineProps<
    MimicComponentInstanceProps &
      TooltipComponentContext<MimicComponentType.PowerConverter> & {
        width?: number | string;
        height?: number | string;
        forceHeight?: boolean;
      }
  >(),
  {
    width: POWER_CONVERTER_WIDTH,
    height: POWER_CONVERTER_HEIGHT,
    forceHeight: true,
  },
);

const { t } = useI18n();
const { getComponentState } = getMimicDataProvider();
const state = getComponentState();
const forwardedProps = reactiveOmit(props, ["registerField", "type"]);
</script>

<template>
  <MimicTooltipTrigger :data="props">
    <AssetBox
      v-bind="forwardedProps"
      :state="state"
    >
      <YardTag>{{ tooltip?.yardTag }}</YardTag>
      <AssetBoxTitle class="gap-2 py-1">
        <component
          :is="POWER_CONVERTER_ICONS[source[0]]"
          class="size-6"
        />
        {{ t(POWER_CONVERTER_TITLES[source[0]]) }}
      </AssetBoxTitle>

      <SensorValue
        :source="source"
        field="active"
      >
        <FieldRenderer.HeatPumpMode />
      </SensorValue>

      <ValueList
        dense
        class="pt-1"
      >
        <ValueListSeparator />
        <ValueListHeatPowerItem :source="sensors.heatTransfer" />
        <ValueListDeltaTItem :source="sensors.heatTransfer" />
        <ValueListTemperatureItem
          v-if="source[0] === SensorComponentType.Brightloop"
          class="text-brand"
          :source="source as ModuleField<SensorComponentType.Brightloop>"
          field="maxChannelTemperature"
          temperature-label="internal"
        />
        <ValueListTemperatureItem
          v-if="source[0] === SensorComponentType.Ugrid"
          class="text-brand"
          :source="source as ModuleField<SensorComponentType.Ugrid>"
          field="tempPowerStage"
          temperature-label="internal"
        />
        <ValueListTemperatureItem
          v-if="source[0] === SensorComponentType.ShorePowerConverter"
          class="text-brand"
          :source="source as ModuleField<SensorComponentType.ShorePowerConverter>"
          field="esiIgbtMaxTemperature"
          temperature-label="internal"
        />
        <ValueListPowerItem
          :source="source"
          field="power"
        />
        <ValueListSeparator />
      </ValueList>
    </AssetBox>
  </MimicTooltipTrigger>
</template>
