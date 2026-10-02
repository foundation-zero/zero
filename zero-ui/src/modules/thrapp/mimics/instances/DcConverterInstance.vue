<script setup lang="ts">
import { first, last } from "lodash";
import { useI18n } from "vue-i18n";
import { MimicComponentInstanceProps } from ".";
import { TooltipComponentContext } from "../../components/tooltip";
import { useDcMode } from "../../state";
import { MimicComponentType } from "../../types";
import { DcMode } from "../components/dc-converter";
import DcConverter from "../components/dc-converter/DcConverter.vue";
import DcConverterStatus from "../components/dc-converter/DcConverterStatus.vue";
import { PvtTitle } from "../components/pvt";
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

const props = defineProps<
  MimicComponentInstanceProps & TooltipComponentContext<MimicComponentType.DcConverter>
>();

const { t } = useI18n();

const { getComponentState } = getMimicDataProvider();
const state = getComponentState();
const modeKey = useDcMode(props.custom.group);
</script>

<template>
  <DcConverter
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
        -
        <FieldRenderer.Source
          v-if="custom.converters.length > 1"
          class="text-3xs text-muted-foreground"
          :source="last(custom.converters)"
        />
      </YardTag>
      <DcConverterStatus :sources="custom.converters" />
    </div>
    <PvtTitle class="gap-2 py-1">
      {{ t(`thrapp.mimics.dc.groups.${props.tooltip?.title}`) }}
    </PvtTitle>
    <DcMode
      :mode="modeKey"
      :state="state"
    />
    <ValueList
      class="gap-0 pt-1"
      dense
    >
      <ValueListSeparator />
      <ValueListHeatPowerItem :source="props.sensors.heatTransfer" />
      <ValueListDeltaTItem :source="props.sensors.heatTransfer" />
      <ValueListTemperatureItem
        class="text-brand"
        :source="props.sensors.temperature"
        temperature-label="internal"
      />
      <ValueListPowerItem :source="props.sensors.power" />

      <ValueListSeparator />
    </ValueList>
  </DcConverter>
</template>
