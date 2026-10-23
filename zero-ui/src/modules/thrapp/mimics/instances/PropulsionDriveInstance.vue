<script setup lang="ts">
import { ZiAradexPropDrive } from "@/modules/common/components/icons";
import { reactiveOmit } from "@vueuse/core";
import { useI18n } from "vue-i18n";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { AssetBox, AssetBoxTitle } from "../components/asset-box";
import { DC_CONVERTER_WIDTH } from "../components/dc-converter";
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
      TooltipComponentContext<MimicComponentType.PropulsionDrive> & {
        width?: number | string;
        height?: number | string;
        forceHeight?: boolean;
      }
  >(),
  {
    width: DC_CONVERTER_WIDTH,
    height: 196,
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
          :source="source"
          field="tempPowerStage"
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
