<script setup lang="ts">
import { ZiPlug3 } from "@/modules/common/components/icons";
import { reactiveOmit } from "@vueuse/core";
import { useI18n } from "vue-i18n";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { AssetBox, AssetBoxTitle } from "../components/asset-box";
import { DC_CONVERTER_WIDTH, DcConverterStatus } from "../components/dc-converter";
import {
  ValueList,
  ValueListDeltaTItem,
  ValueListHeatPowerItem,
  ValueListPowerItem,
  ValueListSeparator,
  ValueListTemperatureItem,
} from "../components/value-list";
import { YardTag } from "../components/yard-tag";
import { getMimicDataProvider, SensorValue } from "../providers";
import { FieldRenderer } from "../renderers";

const props = withDefaults(
  defineProps<
    MimicComponentInstanceProps &
      TooltipComponentContext<MimicComponentType.ShorePowerConverter> & {
        width?: number | string;
        height?: number | string;
        forceHeight?: boolean;
      }
  >(),
  {
    width: DC_CONVERTER_WIDTH,
    height: 222,
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
      <div class="flex items-center justify-between">
        <YardTag class="flex flex-row-reverse items-center gap-0">{{ tooltip?.yardTag }}</YardTag>
        <DcConverterStatus :sources="custom.converters" />
      </div>
      <AssetBoxTitle class="gap-2 py-1">
        <ZiPlug3 class="size-6" />
        {{ t("thrapp.mimics.drives.assets.shorepower") }}
      </AssetBoxTitle>

      <SensorValue
        v-if="source"
        :source="source"
        field="anyActive"
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
          class="text-brand"
          :source="source"
          field="maxEsiIgbtMaxTemperature"
          temperature-label="internal"
        />
        <ValueListPowerItem
          :source="source"
          field="totalPower"
        />
        <ValueListSeparator />
      </ValueList>
    </AssetBox>
  </MimicTooltipTrigger>
</template>
