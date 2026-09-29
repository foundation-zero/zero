<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { useAdvisoryEnabled } from "@/modules/thrapp/state";
import { BoilerTankState } from "@/modules/thrsim/types";
import { computed } from "vue";
import { DHW_TANK_MODE_MODES } from ".";
import { MimicComponentState } from "..";
import { ModeBadge, ModeBadgeSize } from "../mode-badge";

const props = withDefaults(defineProps<{ mode?: BoilerTankState; state?: MimicComponentState }>(), {
  state: MimicComponentState.Normal,
  mode: BoilerTankState.Standby,
});

const badge_mode = computed(() => DHW_TANK_MODE_MODES[props.mode]);

const t = tScoped("thrapp.mimics.boilerTank.modes");

const isAdvisoryEnabled = useAdvisoryEnabled();
</script>

<template>
  <ModeBadge
    v-if="isAdvisoryEnabled && state === MimicComponentState.Normal"
    :mode="badge_mode"
    :label="t(mode)"
    :size="ModeBadgeSize.Tank"
  />
</template>
