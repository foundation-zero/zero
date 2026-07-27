<script setup lang="ts">
import { SensorComponentType, ThrusterMode } from "@/modules/thrs/types";
import { useI18n } from "vue-i18n";
import { MimicComponentInstanceProps } from ".";
import { HeatPump, HeatPumpTitle } from "../components/heat-pump";
import { ValueList, ValueListItem, ValueListSeparator } from "../components/value-list";
import { YardTag } from "../components/yard-tag";
import { getMimicDataProvider, getSensorDefinition, ModuleField } from "../providers";

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
    height: 140,
    forceHeight: true,
  },
);

const { t } = useI18n();
const { getSensorValue, getComponentState } = getMimicDataProvider();

const thruster = getSensorValue(props.source);
const pcs = getSensorValue(props.modeSource);
const temperature = getSensorValue(props.temperatureSource);
const state = getComponentState();
const definition = getSensorDefinition(props.source);

const modeLabelMap: Record<string, string> = {
  [ThrusterMode.Off]: "thrapp.mimics.thrusters.assets.modes.off",
  [ThrusterMode.Propulsion]: "thrapp.mimics.thrusters.assets.modes.propulsion",
  [ThrusterMode.Maneuvering]: "thrapp.mimics.thrusters.assets.modes.maneuvering",
  [ThrusterMode.Regeneration]: "thrapp.mimics.thrusters.assets.modes.regeneration",
};
</script>

<template>
  <HeatPump
    v-bind="props"
    :state="state"
    height="170"
  >
    <YardTag>{{ definition.yardTag }}</YardTag>
    <HeatPumpTitle class="pb-1">
      {{ t(`thrapp.mimics.thrusters.assets.${titleKey}`) }}
    </HeatPumpTitle>

    <span
      class="bg-brand text-background inline-flex w-fit rounded-sm px-2 py-1 text-xs font-semibold"
    >
      {{
        t(
          modeLabelMap[(pcs?.mode?.value as string) ?? ThrusterMode.Off] ??
            "thrapp.mimics.thrusters.assets.modes.off",
        )
      }}
    </span>

    <ValueList class="pt-1">
      <ValueListSeparator />
      <ValueListItem>
        <span>{{ t("thrapp.mimics.thrusters.assets.labels.status") }}</span>
        <strong>{{
          thruster?.active?.value ? t("thrapp.labels.on") : t("thrapp.labels.off")
        }}</strong>
      </ValueListItem>
    </ValueList>
  </HeatPump>
</template>
