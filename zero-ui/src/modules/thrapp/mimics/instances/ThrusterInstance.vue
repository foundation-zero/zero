<script setup lang="ts">
import { SensorComponentType, ThrusterMode } from "@/modules/thrsim/types";
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { MimicComponentInstanceProps } from ".";
import { TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { HeatPump, HeatPumpTitle } from "../components/heat-pump";
import { ModeBadge, ModeBadgeMode, ModeBadgeSize } from "../components/mode-badge";
import {
  ValueList,
  ValueListDeltaTItem,
  ValueListHeatPowerItem,
  ValueListSeparator,
  ValueListTemperatureItem,
} from "../components/value-list";
import { YardTag } from "../components/yard-tag";
import { getMimicDataProvider, getSensorDefinition, ModuleField } from "../providers";
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
const { getSensorValue, getComponentState } = getMimicDataProvider();

const pcs = getSensorValue(props.sensors.pcs);
const state = getComponentState();
const definition = getSensorDefinition(props.source[1], props.source[2]);

const modeLabelMap = {
  [ThrusterMode.Off]: {
    mode: ModeBadgeMode.Active,
    label: t("thrapp.mimics.thrusters.assets.modes.off"),
  },
  [ThrusterMode.Propulsion]: {
    mode: ModeBadgeMode.Active,
    label: t("thrapp.mimics.thrusters.assets.modes.propulsion"),
  },
  [ThrusterMode.Maneuvering]: {
    mode: ModeBadgeMode.Active,
    label: t("thrapp.mimics.thrusters.assets.modes.maneuvering"),
  },
  [ThrusterMode.Regeneration]: {
    mode: ModeBadgeMode.Active,
    label: t("thrapp.mimics.thrusters.assets.modes.regeneration"),
  },
};

const mode = computed(() => {
  const modeKey = (pcs?.value?.mode?.value as ThrusterMode) ?? ThrusterMode.Off;
  return modeLabelMap[modeKey];
});
const tempSource = [
  SensorComponentType.Temperature,
  "thrusters",
  "placeholder",
] as unknown as ModuleField<SensorComponentType.Temperature>;
</script>

<template>
  <HeatPump
    v-bind="props"
    :state="state"
  >
    <YardTag>{{ definition.yardTag }}</YardTag>
    <HeatPumpTitle class="pb-1">
      {{ t(`thrapp.mimics.thrusters.assets.${custom.titleKey}`) }}
    </HeatPumpTitle>
    <ModeBadge
      v-bind="mode"
      :size="ModeBadgeSize.Asset"
    />

    <ValueList class="pt-1">
      <ValueListSeparator />

      <SensorValue :source="props.source">
        <ValueListItem class="text-brand">
          <span class="flex items-center gap-0.5"> Power </span>
          <span></span>
        </ValueListItem>
      </SensorValue>
      <ValueListTemperatureItem
        class="text-brand"
        :source="tempSource"
        temperature-label="internal"
      />
      <ValueListHeatPowerItem :source="props.sensors.heatTransfer" />
      <ValueListDeltaTItem :source="props.sensors.heatTransfer" />

      <ValueListSeparator />
    </ValueList>
  </HeatPump>
</template>
