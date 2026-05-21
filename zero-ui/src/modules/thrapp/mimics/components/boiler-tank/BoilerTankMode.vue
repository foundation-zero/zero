<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";
import { BOILER_TANK_MODE_COLORS, BoilerTankModes } from ".";

const props = defineProps<{ mode: BoilerTankModes }>();

const color = computed(() => BOILER_TANK_MODE_COLORS[props.mode]);

const { t } = useI18n();
</script>

<template>
  <div
    class="text-inverse-foreground bg-attention inline rounded-md px-2 py-0.5 text-sm font-medium transition-colors"
    :style="{
      backgroundColor: color,
    }"
  >
    {{ t(`thrapp.mimics.boilerTank.modes.${props.mode}`) }}
  </div>
</template>
