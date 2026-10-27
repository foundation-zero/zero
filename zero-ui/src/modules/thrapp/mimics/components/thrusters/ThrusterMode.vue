<script setup lang="ts">
import { SensorComponentType, ThrusterMode } from "@/modules/thrapp/types/thrs";
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { getMimicDataProvider, ModuleField } from "../../providers";
import { ModeBadge, ModeBadgeMode, ModeBadgeSize } from "../mode-badge";

const props = withDefaults(defineProps<{ source: ModuleField<SensorComponentType.Pcs> }>(), {});

const { t } = useI18n();
const { getSensorValue } = getMimicDataProvider();

const pcs = getSensorValue(props.source);

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
  <ModeBadge
    v-bind="mode"
    :size="ModeBadgeSize.Asset"
  />
</template>
