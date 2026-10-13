<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrsim/types";
import { useI18n } from "vue-i18n";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { AssetBox, AssetBoxTitle } from "../components/asset-box";
import { ThrusterMode } from "../components/thrusters";
import {
  ValueList,
  ValueListDeltaTItem,
  ValueListHeatPowerItem,
  ValueListItem,
  ValueListSeparator,
  ValueListTemperatureItem,
} from "../components/value-list";
import { YardTag } from "../components/yard-tag";
import { getField, getMimicDataProvider } from "../providers";
import SensorValue from "../providers/SensorValue.vue";

const props = withDefaults(
  defineProps<
    MimicComponentInstanceProps &
      TooltipComponentContext<MimicComponentType.Thruster> & {
        width?: number | string;
        height?: number | string;
        forceHeight?: boolean;
      }
  >(),
  {
    width: 180,
    height: 225,
    forceHeight: true,
  },
);

const { t } = useI18n();
const { getComponentState } = getMimicDataProvider();

const state = getComponentState();
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.Thruster"
    :data="props"
  >
    <AssetBox
      v-bind="props"
      :state="state"
    >
      <YardTag>{{ tooltip?.yardTag }}</YardTag>
      <AssetBoxTitle class="pb-1">
        {{ t(`thrapp.mimics.thrusters.assets.${custom.titleKey}`) }}
      </AssetBoxTitle>

      <ThrusterMode :source="sensors.pcs" />

      <ValueList
        dense
        class="pt-1"
      >
        <ValueListSeparator />

        <ValueListHeatPowerItem :source="sensors.heatTransfer" />
        <ValueListDeltaTItem :source="sensors.heatTransfer" />
        <ValueListTemperatureItem
          class="text-brand"
          :source="getField(SensorComponentType.Temperature, 'thrusters', 'placeholder')"
          temperature-label="internal"
        />
        <SensorValue :source="source">
          <ValueListItem class="text-brand">
            <span class="flex items-center gap-0.5"> Power </span>
            <span></span>
          </ValueListItem>
        </SensorValue>

        <ValueListSeparator />
      </ValueList>
    </AssetBox>
  </MimicTooltipTrigger>
</template>
