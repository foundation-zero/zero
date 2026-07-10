<script setup lang="ts">
import { MimicComponentBaseProps, MimicComponentState } from "..";
import MimicComponent from "../MimicComponent.vue";
import {
  ACTUATED_VALVE_BASE_ORIENTATION,
  ACTUATED_VALVE_HEIGHT,
  ACTUATED_VALVE_WIDTH,
} from "./index";

withDefaults(defineProps<MimicComponentBaseProps>(), {
  orientation: ACTUATED_VALVE_BASE_ORIENTATION,
});
</script>

<template>
  <MimicComponent
    :width="ACTUATED_VALVE_WIDTH"
    :height="ACTUATED_VALVE_HEIGHT"
    :base-orientation="ACTUATED_VALVE_BASE_ORIENTATION"
    :orientation="orientation"
    :rotation="rotation"
    :state="state"
    data-slot="actuated-valve"
  >
    <template #default="{ stateColor, state }">
      <slot />
      <circle
        cx="18"
        cy="18"
        r="2"
        :fill="stateColor"
        :stroke="stateColor"
        :stroke-width="state === MimicComponentState.Normal ? 0 : 2"
      />

      <path
        d="M17.1992 12.3999H18.7992L18.7992 16.3999H17.1992L17.1992 12.3999Z"
        :fill="stateColor"
      />
    </template>
  </MimicComponent>
</template>
