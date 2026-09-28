<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { computed } from "vue";
import { HEAT_PUMP_MODE_COLORS, HeatPumpModes } from ".";
import { MimicComponentState } from "..";
import { ModeBadgeSize } from "../mode-badge";
import ModeBadge from "../mode-badge/ModeBadge.vue";

const props = withDefaults(defineProps<{ mode: HeatPumpModes; state?: MimicComponentState }>(), {
  state: MimicComponentState.Normal,
});

const color = computed(() => {
  if (props.state === MimicComponentState.Normal) {
    return HEAT_PUMP_MODE_COLORS[props.mode];
  } else {
    return HEAT_PUMP_MODE_COLORS[props.state];
  }
});

const t = tScoped("thrapp.mimics.heatPump.modes");
</script>

<template>
  <ModeBadge
    :mode="color"
    :label="t(mode)"
    :size="ModeBadgeSize.Asset"
  />
</template>
