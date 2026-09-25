<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { useAdvisoryEnabled } from "@/modules/thrapp/state";
import { PvtMode } from "@/modules/thrsim/types";
import { computed } from "vue";
import { PVT_MODE_COLORS } from ".";
import { MimicComponentState } from "..";
import { ModeBadge, ModeBadgeSize } from "../mode-badge";

const props = withDefaults(defineProps<{ mode: PvtMode; state?: MimicComponentState }>(), {
  state: MimicComponentState.Normal,
});

const badge_mode = computed(() => PVT_MODE_COLORS[props.mode]);

const t = tScoped("thrapp.mimics.pvt.assets.modes");

const isAdvisoryEnabled = useAdvisoryEnabled();
</script>

<template>
  <ModeBadge
    v-if="isAdvisoryEnabled && state == MimicComponentState.Normal"
    :mode="badge_mode"
    :label="t(mode)"
    :size="ModeBadgeSize.Asset"
  />
</template>
