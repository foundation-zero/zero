<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { useAdvisoryEnabled } from "@/modules/thrapp/state";
import { DcMode } from "@/modules/thrsim/types";
import { computed } from "vue";
import { DC_MODE_COLORS } from ".";
import { MimicComponentState } from "..";
import { ModeBadge, ModeBadgeSize } from "../mode-badge";

const props = withDefaults(defineProps<{ mode: DcMode; state?: MimicComponentState }>(), {
  state: MimicComponentState.Normal,
});

const badgeMode = computed(() => DC_MODE_COLORS[props.mode]);

const t = tScoped("thrapp.mimics.dc.assets.modes");

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
