<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import { computed } from "vue";
import { CHARGE_STATE_COLORS, ChargeState, PcmChargeStateProps } from ".";
import Placeholder from "../../renderers/PlaceholderRenderer.vue";

const props = defineProps<PcmChargeStateProps>();

const color = computed(() => CHARGE_STATE_COLORS[props.state ?? ChargeState.Empty]);
const t = tScoped("thrapp.mimics.pcm.states");
</script>

<template>
  <span
    class="text-inverse-foreground w-fit rounded-lg px-2 text-sm font-medium"
    :style="{ backgroundColor: color }"
  >
    <Placeholder v-if="!state" />
    <slot v-else> {{ t(state) }} </slot>
  </span>
</template>
