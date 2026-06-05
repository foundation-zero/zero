<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { computed } from "vue";
import { HEAT_PUMP_MODE_COLORS, HeatPumpModes } from ".";
import { MimicComponentState } from "..";

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
  <div
    class="text-inverse-foreground bg-attention inline rounded-md px-2 py-0.5 text-sm font-medium transition-colors"
    :style="{
      backgroundColor: color,
    }"
  >
    <span v-if="state === MimicComponentState.Normal">{{ t(mode) }}</span>
    <span v-else>{{ t(state) }}</span>
  </div>
</template>
