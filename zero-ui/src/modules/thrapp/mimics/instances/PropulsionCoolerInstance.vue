<script setup lang="ts">
import { RiSnowflakeLine } from "@remixicon/vue";
import { useI18n } from "vue-i18n";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { AssetBox, AssetBoxTitle } from "../components/asset-box";
import { DC_CONVERTER_HEIGHT, DC_CONVERTER_WIDTH } from "../components/dc-converter";
import {
  ValueList,
  ValueListDeltaTItem,
  ValueListHeatPowerItem,
  ValueListSeparator,
} from "../components/value-list";
import { YardTag } from "../components/yard-tag";
import { getMimicDataProvider } from "../providers";

const props = withDefaults(
  defineProps<
    MimicComponentInstanceProps &
      TooltipComponentContext<MimicComponentType.PropulsionCooler> & {
        width?: number | string;
        height?: number | string;
        forceHeight?: boolean;
        dense?: boolean;
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
    :type="MimicComponentType.PropulsionCooler"
    :data="props"
  >
    <AssetBox
      v-bind="props"
      :state="state"
      class="pt-2"
    >
      <YardTag>{{ tooltip?.yardTag }}</YardTag>
      <AssetBoxTitle class="gap-2">
        <RiSnowflakeLine class="text-brand" />
        {{ t(`thrapp.mimics.drives.assets.propulsionCooler.${tooltip?.title}`) }}
      </AssetBoxTitle>

      <ValueList
        dense
        class="pt-1"
      >
        <ValueListSeparator />

        <ValueListHeatPowerItem :source="sensors.heatTransfer" />
        <ValueListDeltaTItem :source="sensors.heatTransfer" />
        <ValueListSeparator />
      </ValueList>
    </AssetBox>
  </MimicTooltipTrigger>
</template>
