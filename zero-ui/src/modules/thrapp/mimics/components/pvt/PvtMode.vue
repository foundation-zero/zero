<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { PvtMode } from "@/modules/thrsim/types";
import { computed } from "vue";
import { PVT_MODE_COLORS } from ".";
import { MimicComponentState } from "..";

const props = withDefaults(defineProps<{ mode: PvtMode; state?: MimicComponentState }>(), {
  state: MimicComponentState.Normal,
});

const color = computed(() => {
  if (props.state === MimicComponentState.Normal) {
    return PVT_MODE_COLORS[props.mode];
  } else {
    return PVT_MODE_COLORS[props.state];
  }
});

const t = tScoped("thrapp.mimics.pvt.assets.modes");
</script>

<template>
  <div
    class="text-inverse-foreground bg-attention inline rounded-md px-2 py-0.5 text-sm font-medium transition-colors"
    :style="{
      backgroundColor: color,
    }"
  >
    <span v-if="state === MimicComponentState.Normal">{{ t(mode.toLowerCase()) }}</span>
    <span v-else>{{ t(state) }}</span>
  </div>
</template>
