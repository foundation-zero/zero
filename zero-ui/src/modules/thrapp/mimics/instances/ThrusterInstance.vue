<script setup lang="ts">
import { SensorComponentType, ThrusterMode } from "@/modules/thrsim/types";
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { AssetBox, AssetBoxTitle } from "../components/asset-box";
import { ModeBadge, ModeBadgeMode, ModeBadgeSize } from "../components/mode-badge";
import {
  ValueList,
  ValueListDeltaTItem,
  ValueListHeatPowerItem,
  ValueListItem,
  ValueListSeparator,
  ValueListTemperatureItem,
} from "../components/value-list";
import { YardTag } from "../components/yard-tag";
import { getMimicDataProvider, ModuleField } from "../providers";
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

      <ModeBadge
        v-bind="mode"
        :size="ModeBadgeSize.Asset"
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
          :source="tempSource"
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
