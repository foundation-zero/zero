<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { HEAT_PUMP_MODE_COLORS, HeatPumpModes } from ".";

const props = defineProps<{ mode: HeatPumpModes }>();

const color = computed(() => HEAT_PUMP_MODE_COLORS[props.mode]);

const { t } = useI18n();
</script>

<template>
  <div
    class="text-inverse-foreground bg-attention inline rounded-md px-2 py-0.5 text-sm font-medium transition-colors"
    :style="{
      backgroundColor: color,
    }"
  >
    {{ t(`thrapp.mimics.heatPump.modes.${props.mode}`) }}
  </div>
</template>
