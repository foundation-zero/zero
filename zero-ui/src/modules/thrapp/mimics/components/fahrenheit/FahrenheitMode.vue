<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { computed } from "vue";
import { getMimicDataProvider, ModuleField } from "../../providers";
import { ModeBadge, ModeBadgeMode, ModeBadgeSize } from "../mode-badge";

const props = defineProps<{ source: ModuleField<SensorComponentType.AdsorptionChiller> }>();

const t = tScoped("thrapp.mimics.adsorption.chiller.modes");
const { getSensorValue } = getMimicDataProvider();

const chiller = getSensorValue(props.source);

const mode = computed(() => {
  if (chiller?.value?.freeCooling?.value) {
    return { mode: ModeBadgeMode.Cooling, label: t("freeCooling") };
  } else if (chiller?.value?.operating?.value) {
    return { mode: ModeBadgeMode.Cooling, label: t("cooling") };
  }
  return { mode: ModeBadgeMode.Idle, label: t("idle") };
});
</script>

<template>
  <ModeBadge
    v-bind="mode"
    :size="ModeBadgeSize.Asset"
  />
</template>
