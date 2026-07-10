<script setup lang="ts">
import { SensorComponentType } from "@/modules/thrs/types";
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { MimicComponentInstanceProps } from ".";
import { HeatPump, HeatPumpTitle } from "../components/heat-pump";
import {
  ValueList,
  ValueListDeltaTItem,
  ValueListFlowItem,
  ValueListItem,
  ValueListSeparator,
  ValueListTemperatureItem,
} from "../components/value-list";
import { YardTag } from "../components/yard-tag";
import { getMimicDataProvider, ModuleField } from "../providers";

const props = withDefaults(
  defineProps<
    MimicComponentInstanceProps & {
      pumpSource: ModuleField<SensorComponentType.Pump, "pvt">;
      flowSource: ModuleField<SensorComponentType.Flow, "pvt">;
      returnTemperatureSource: ModuleField<SensorComponentType.Temperature, "pvt">;
      supplyTemperatureSource: ModuleField<SensorComponentType.Temperature, "pvt">;
      titleKey: "fwdTitle" | "aftTitle" | "ownersTitle";
      tagId: string;
      width?: number | string;
      height?: number | string;
      forceHeight?: boolean;
    }
  >(),
  {
    width: 220,
    height: 228,
    forceHeight: true,
  },
);

const { t } = useI18n();
const { getSensorValue, getComponentState } = getMimicDataProvider();

const pump = getSensorValue(props.pumpSource);
const flow = getSensorValue(props.flowSource);
const returnTemp = getSensorValue(props.returnTemperatureSource);
const supplyTemp = getSensorValue(props.supplyTemperatureSource);
const state = getComponentState();

const deltaT = computed(() => {
  const inValue = supplyTemp.value?.temperature?.value;
  const outValue = returnTemp.value?.temperature?.value;
  if (inValue == null || outValue == null) return undefined;
  return inValue - outValue;
});

const modeKey = computed(() => {
  const active = (pump.value?.flow?.value ?? 0) > 0;
  return active
    ? "thrapp.mimics.pvt.assets.modes.harvesting"
    : "thrapp.mimics.pvt.assets.modes.idle";
});
</script>

<template>
  <HeatPump
    v-bind="props"
    :state="state"
    :height="228"
  >
    <YardTag>{{ tagId }}</YardTag>
    <HeatPumpTitle class="pb-1">
      {{ t(`thrapp.mimics.pvt.assets.${titleKey}`) }}
    </HeatPumpTitle>

    <span
      class="bg-brand text-background inline-flex w-fit rounded-sm px-2 py-1 text-xs font-semibold"
    >
      {{ t(modeKey) }}
    </span>

    <ValueList class="pt-1">
      <ValueListSeparator />
      <ValueListFlowItem :value="flow?.flow?.value" />
      <ValueListTemperatureItem
        :label="t('thrapp.mimics.pvt.assets.labels.temperature')"
        :value="returnTemp?.temperature?.value"
      />
      <ValueListDeltaTItem :value="deltaT" />
      <ValueListItem>
        <span>{{ t("thrapp.mimics.pvt.assets.labels.power") }}</span>
        <strong>{{ Math.round(pump?.speed?.value ?? 0) }} %</strong>
      </ValueListItem>
      <ValueListSeparator />
    </ValueList>
  </HeatPump>
</template>
