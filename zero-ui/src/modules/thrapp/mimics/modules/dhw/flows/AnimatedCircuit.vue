<script setup lang="ts">
import { VALVE_OPEN_THRESHOLD } from "@/modules/thrapp/utils/consts";
import { SensorComponentType } from "@/modules/thrs/types";
import { computed } from "vue";
import { getMimicDataProvider, ModuleField } from "../../../providers";

const props = defineProps<{
  flow: ModuleField<SensorComponentType.Flow | SensorComponentType.CalculatedFlow>[];
}>();

const { getSensorValue } = getMimicDataProvider();

const flowValues = props.flow.map(getSensorValue);

const highestFlow = computed(() => {
  const flows = flowValues.map((valve) => valve.value?.flow.value ?? 0);
  return Math.max(...flows);
});
</script>

<template>
  <g
    class="transition-1000 transition-opacity"
    :class="{
      'flow animate-pulse': highestFlow >= VALVE_OPEN_THRESHOLD,
      'opacity-0': highestFlow < VALVE_OPEN_THRESHOLD,
    }"
    :style="{
      '--flow-width': 2, // 1 + 3 * highestFlow,
    }"
  >
    <slot />
  </g>
</template>

<style scoped>
g {
  will-change: opacity;
}

:deep(path) {
  will-change: stroke-width;
}

.flow :deep(path) {
  animation: flow 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
