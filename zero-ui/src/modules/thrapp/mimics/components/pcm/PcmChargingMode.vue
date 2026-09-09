<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { computed } from "vue";
import { CHARGING_MODE_COLORS, ChargingMode, PcmChargingModeProps } from ".";
import { FieldRenderer } from "../../renderers";

const props = defineProps<PcmChargingModeProps>();

const color = computed(() => CHARGING_MODE_COLORS[props.mode ?? ChargingMode.Idle]);

const t = tScoped("thrapp.mimics.pcm.modes");
</script>

<template>
  <span
    class="text-inverse-foreground w-fit rounded-lg px-2 text-sm font-medium"
    :style="{ backgroundColor: color }"
  >
    <FieldRenderer.Placeholder v-if="!mode" />
    <slot v-else> {{ t(mode) }} </slot>
  </span>
</template>
