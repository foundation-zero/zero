<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { useAdvisoryEnabled } from "@/modules/heat/state";
import { PvtMode } from "@/modules/heat-simulation/types";
import { computed } from "vue";
import { PVT_MODE_COLORS } from ".";
import { MimicComponentState } from "..";
import { ModeBadge, ModeBadgeSize } from "../mode-badge";

const props = withDefaults(defineProps<{ mode: PvtMode; state?: MimicComponentState }>(), {
  state: MimicComponentState.Normal,
});

const badgeMode = computed(() => PVT_MODE_COLORS[props.mode]);

const t = tScoped("heat.mimics.pvt.assets.modes");

const isAdvisoryEnabled = useAdvisoryEnabled();
</script>

<template>
  <ModeBadge
    v-if="isAdvisoryEnabled && state == MimicComponentState.Normal"
    :mode="badgeMode"
    :label="t(mode)"
    :size="ModeBadgeSize.Asset"
  />
</template>
