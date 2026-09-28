<script setup lang="ts">
import { SensorComponentType, ThrusterMode } from "@/modules/thrsim/types";
import { RiDropLine, RiFireLine } from "@remixicon/vue";
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { MimicComponentInstanceProps } from ".";
import { HeatPump, HeatPumpTitle } from "../components/heat-pump";
import { ModeBadge, ModeBadgeMode, ModeBadgeSize } from "../components/mode-badge";
import { ValueList, ValueListItem, ValueListSeparator } from "../components/value-list";
import { YardTag } from "../components/yard-tag";
import { getMimicDataProvider, getSensorDefinition, ModuleField } from "../providers";
import { FieldRenderer } from "../renderers";

const props = withDefaults(
  defineProps<
    MimicComponentInstanceProps & {
      source: ModuleField<SensorComponentType.Thruster, "thrusters">;
      modeSource: ModuleField<SensorComponentType.Pcs, "thrusters">;
      temperatureSource: ModuleField<SensorComponentType.Temperature, "thrusters">;
      titleKey: "aftTitle" | "fwdTitle";
      width?: number | string;
      height?: number | string;
      forceHeight?: boolean;
    }
  >(),
  {
    width: 180,
    height: 250,
    forceHeight: true,
  },
);

const { t } = useI18n();
const { getSensorValue, getComponentState } = getMimicDataProvider();

const pcs = getSensorValue(props.modeSource);
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
</script>

<template>
  <HeatPump
    v-bind="props"
    :state="state"
  >
    <YardTag>{{ definition.yardTag }}</YardTag>
    <HeatPumpTitle class="pb-1">
      {{ t(`thrapp.mimics.thrusters.assets.${titleKey}`) }}
    </HeatPumpTitle>
    <ModeBadge
      v-bind="mode"
      :size="ModeBadgeSize.Asset"
    />

    <ValueList class="pt-1">
      <ValueListSeparator />
      <ValueListItem>
        <span class="flex items-center gap-0.5"> Power </span>
        <span></span>
      </ValueListItem>

      <ValueListItem>
        <span class="flex items-center gap-0.5"> Internal Temp </span>
        <span></span>
      </ValueListItem>

      <ValueListItem>
        <span class="text-brand text-sm">{{ t("units.deltaT") }}</span>
        <span class="text-foreground font-medium">
          <FieldRenderer.Placeholder />
        </span>
      </ValueListItem>
      <ValueListItem>
        <span class="flex items-center gap-0.5">
          <RiDropLine class="text-brand size-3.5" />
        </span>
        <span class="text-foreground font-medium">
          <FieldRenderer.Placeholder />
        </span>
      </ValueListItem>
      <ValueListItem>
        <span class="flex items-center gap-0.5">
          <RiFireLine class="text-heating-medium size-3.5" />
        </span>
        <span class="text-foreground font-medium">
          <FieldRenderer.Placeholder />
        </span>
      </ValueListItem>

      <ValueListSeparator />
    </ValueList>
  </HeatPump>
</template>
