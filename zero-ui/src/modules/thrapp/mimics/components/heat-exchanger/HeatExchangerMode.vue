<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { computed } from "vue";
import { HEATING_STATE_COLORS, HeatingState } from "..";

const props = withDefaults(defineProps<{ state?: HeatingState }>(), {
  state: HeatingState.Idle,
});

const color = computed(() => HEATING_STATE_COLORS[props.state]);

const t = tScoped("thrapp.mimics.heatExchanger.modes");
</script>

<template>
  <div
    class="text-inverse-foreground bg-attention inline rounded-md px-2 py-0.5 text-sm font-medium transition-colors"
    :style="{
      backgroundColor: color,
    }"
  >
    <span>{{ t(state) }}</span>
  </div>
</template>
