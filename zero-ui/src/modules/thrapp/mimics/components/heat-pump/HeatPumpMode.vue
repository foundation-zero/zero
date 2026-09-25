<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { computed } from "vue";
import { HEAT_PUMP_MODE_COLORS, HeatPumpModes } from ".";
import { MimicComponentState } from "..";
import { ModeBadge, ModeBadgeSize } from "../mode-badge";

const props = withDefaults(defineProps<{ mode: HeatPumpModes; state?: MimicComponentState }>(), {
  state: MimicComponentState.Normal,
});

const badge_mode = computed(() => HEAT_PUMP_MODE_COLORS[props.mode]);

const t = tScoped("thrapp.mimics.heatPump.modes");
</script>

<template>
  <ModeBadge
    :mode="badge_mode"
    :label="t(mode)"
    :size="ModeBadgeSize.Asset"
  />
</template>
