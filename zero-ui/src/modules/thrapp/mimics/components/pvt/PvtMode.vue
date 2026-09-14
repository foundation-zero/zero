<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { PvtMode } from "@/modules/thrsim/types";
import { computed } from "vue";
import { MimicComponentState } from "..";
import { ModeBadge, ModeBadgeMode, ModeBadgeSize } from "../mode-badge";

const props = withDefaults(defineProps<{ mode: PvtMode; state?: MimicComponentState }>(), {
  state: MimicComponentState.Normal,
});

const t = tScoped("thrapp.mimics.pvt.assets.modes");

const modes = computed(() => {
  if (props.state == MimicComponentState.Manual) return { mode: ModeBadgeMode.ManualControl };
  if (props.mode == PvtMode.Recovery) return { mode: ModeBadgeMode.Using, label: t("recovery") };
  else return { mode: ModeBadgeMode.Idle, label: t("idle") };
});
</script>

<template>
  <ModeBadge
    v-bind="modes"
    :size="ModeBadgeSize.Asset"
  />
</template>
