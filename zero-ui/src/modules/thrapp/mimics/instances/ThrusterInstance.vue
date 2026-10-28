<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { ZiThrusters } from "@/modules/common/components/icons";
import { RiFlashlightLine } from "@remixicon/vue";
import { reactiveOmit } from "@vueuse/core";
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
import { FieldRenderer } from "../renderers";

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
    width: 200,
    height: 205,
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
        <ZiThrusters />
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
          <ValueListItem>
            <span class="flex items-center gap-0.5">
              <RiFlashlightLine class="text-constructive size-3.5" />
            </span>
            <span class="text-foreground font-medium">
              <FieldRenderer.Placeholder />
            </span>
          </ValueListItem>
        </SensorValue>

        <ValueListSeparator />
      </ValueList>
    </AssetBox>
  </MimicTooltipTrigger>
</template>
