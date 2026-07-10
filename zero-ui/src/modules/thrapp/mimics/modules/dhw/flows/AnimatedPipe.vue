<script setup lang="ts">
import { VALVE_OPEN_THRESHOLD } from "@/modules/thrapp/utils/consts";
import { SensorComponentType } from "@/modules/thrs/types";
import { computed } from "vue";
import { getMimicDataProvider, ModuleField } from "../../../providers";

const props = defineProps<{
  valves: ModuleField<SensorComponentType.Valve>[];
}>();

const { getSensorValue } = getMimicDataProvider();

const valves = props.valves.map(getSensorValue);

const highestFlow = computed(() => {
  const positions = valves.map((valve) => valve.value?.positionRel.value ?? 0);
  return Math.max(...positions);
});
</script>

<template>
  <g
    class="transition-opacity duration-1000"
    :class="{
      'opacity-100': highestFlow >= VALVE_OPEN_THRESHOLD,
      'opacity-0': highestFlow < VALVE_OPEN_THRESHOLD,
    }"
  >
    <slot />
  </g>
</template>
