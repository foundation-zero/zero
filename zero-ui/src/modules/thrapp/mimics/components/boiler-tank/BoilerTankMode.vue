<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { BoilerTankState } from "@/modules/thrsim/types";
import { computed } from "vue";
import { DHW_TANK_MODE_MODES } from ".";
import { MimicComponentState } from "..";
import { ModeBadge, ModeBadgeSize } from "../mode-badge";

const props = withDefaults(defineProps<{ mode?: BoilerTankState; state?: MimicComponentState }>(), {
  state: MimicComponentState.Normal,
  mode: BoilerTankState.Standby,
});

const mode = computed(() => {
  if (props.state === MimicComponentState.Normal) {
    return DHW_TANK_MODE_MODES[props.mode];
  } else {
    return DHW_TANK_MODE_MODES[props.state];
  }
});

const t = tScoped("thrapp.mimics.boilerTank.modes");
</script>

<template>
  <ModeBadge
    :mode="mode"
    :label="t(props.mode.toString())"
    :size="ModeBadgeSize.Tank"
  />
</template>
