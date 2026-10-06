<script setup lang="ts">
import { ZiDcConverter } from "@/modules/common/components/icons";
import { first, last } from "lodash";
import { useI18n } from "vue-i18n";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { useDcMode } from "../../state";
import { MimicComponentType } from "../../types";
import { AssetBox, AssetBoxTitle } from "../components/asset-box";
import { DC_CONVERTER_HEIGHT, DC_CONVERTER_WIDTH, DcMode } from "../components/dc-converter";
import DcConverterStatus from "../components/dc-converter/DcConverterStatus.vue";
import {
  ValueList,
  ValueListDeltaTItem,
  ValueListHeatPowerItem,
  ValueListPowerItem,
  ValueListSeparator,
  ValueListTemperatureItem,
} from "../components/value-list";
import { YardTag } from "../components/yard-tag";
import { getMimicDataProvider } from "../providers";
import { FieldRenderer } from "../renderers";

const props = withDefaults(
  defineProps<
    MimicComponentInstanceProps &
      TooltipComponentContext<MimicComponentType.DcConverter> & {
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

const modeKey = useDcMode(props.custom.group);
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.DcConverter"
    :data="props"
  >
    <AssetBox
      v-bind="props"
      :state="state"
    >
      <div class="flex items-center justify-between">
        <YardTag class="flex flex-row-reverse items-center gap-0">
          <FieldRenderer.Source
            v-if="custom.converters.length"
            class="text-3xs text-muted-foreground"
            :source="first(custom.converters)"
          />
          <template v-if="custom.converters.length > 1">
            -
            <FieldRenderer.Source
              class="text-3xs text-muted-foreground"
              :source="last(custom.converters)"
            />
          </template>
        </YardTag>
        <DcConverterStatus :sources="custom.converters" />
      </div>
      <AssetBoxTitle class="gap-2 py-1">
        <slot name="icon">
          <ZiDcConverter />
        </slot>
        {{ t(`thrapp.mimics.dc.groups.${tooltip?.title}`) }}
      </AssetBoxTitle>

      <DcMode
        :mode="modeKey"
        :state="state"
      />

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
