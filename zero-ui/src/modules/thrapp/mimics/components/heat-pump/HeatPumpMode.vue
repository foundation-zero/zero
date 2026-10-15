<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { computed } from "vue";
import { HEAT_PUMP_MODE_COLORS, HeatPumpModes } from ".";
import { MimicComponentState } from "..";
import { ModeBadge, ModeBadgeSize } from "../mode-badge";

const props = withDefaults(
  defineProps<{ mode: HeatPumpModes; state?: MimicComponentState; icon?: boolean }>(),
  {
    state: MimicComponentState.Normal,
  },
);

const badgeMode = computed(() => HEAT_PUMP_MODE_COLORS[props.mode]);

const t = tScoped("thrapp.mimics.heatPump.modes");
</script>

<template>
  <ModeBadge
    :icon="icon"
    :mode="badgeMode"
    :label="t(mode)"
    :size="ModeBadgeSize.Asset"
  />
</template>
