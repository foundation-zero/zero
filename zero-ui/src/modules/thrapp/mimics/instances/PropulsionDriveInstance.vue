<script setup lang="ts">
import { ZiAradexPropDrive } from "@/modules/common/components/icons";
import { useI18n } from "vue-i18n";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip/index.ts";
import { MimicComponentType } from "../../types/index.ts";
import { AssetBox, AssetBoxTitle } from "../components/asset-box/index.ts";
import { DC_CONVERTER_HEIGHT, DC_CONVERTER_WIDTH } from "../components/dc-converter/index.ts";
import {
  ValueList,
  ValueListDeltaTItem,
  ValueListHeatPowerItem,
  ValueListPowerItem,
  ValueListSeparator,
  ValueListTemperatureItem,
} from "../components/value-list/index.ts";
import { YardTag } from "../components/yard-tag/index.ts";
import { getMimicDataProvider, SensorValue } from "../providers/index.ts";
import { FieldRenderer } from "../renderers/index.ts";
import { MimicComponentInstanceProps } from "./index.ts";

const props = withDefaults(
  defineProps<
    MimicComponentInstanceProps &
      TooltipComponentContext<MimicComponentType.PropulsionDrive> & {
        width?: number | string;
        height?: number | string;
        forceHeight?: boolean;
      }
  >(),
  {
    width: DC_CONVERTER_WIDTH,
    height: DC_CONVERTER_HEIGHT,
    forceHeight: true,
  },
);

const { t } = useI18n();

const { getComponentState } = getMimicDataProvider();

const state = getComponentState();
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.PropulsionDrive"
    :data="props"
  >
    <AssetBox
      v-bind="props"
      :state="state"
    >
      <YardTag>{{ tooltip?.yardTag }}</YardTag>

      <AssetBoxTitle class="gap-2 py-1 text-xs">
        <ZiAradexPropDrive />
        {{ t(`thrapp.mimics.drives.assets.propulsionDrive`) }}
      </AssetBoxTitle>

      <SensorValue
        v-if="source"
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
          class="text-brand"
          :source="sensors.temperature"
          temperature-label="internal"
        />
        <ValueListPowerItem :source="sensors.power" />

        <ValueListSeparator />
      </ValueList>
    </AssetBox>
  </MimicTooltipTrigger>
</template>
