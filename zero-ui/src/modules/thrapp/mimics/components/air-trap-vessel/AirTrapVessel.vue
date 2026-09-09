<script setup lang="ts">
import { MimicComponentBaseProps } from "..";
import MimicComponent from "../MimicComponent.vue";
import {
  AIR_TRAP_VESSEL_BASE_ORIENTATION,
  AIR_TRAP_VESSEL_HEIGHT,
  AIR_TRAP_VESSEL_WIDTH,
} from "./index";

withDefaults(defineProps<MimicComponentBaseProps>(), {
  orientation: () => AIR_TRAP_VESSEL_BASE_ORIENTATION,
});
</script>

<template>
  <MimicComponent
    :width="AIR_TRAP_VESSEL_WIDTH"
    :height="AIR_TRAP_VESSEL_HEIGHT"
    :base-orientation="AIR_TRAP_VESSEL_BASE_ORIENTATION"
    :orientation="orientation"
    data-slot="air-trap-vessel"
    :state="state"
  >
    <line
      x1="13.7479"
      y1="22.7649"
      x2="13.7479"
      y2="0.877075"
      stroke="#5685A9"
    />
    <rect
      x="23.2837"
      y="22.3739"
      width="39"
      height="19"
      transform="rotate(90 23.2837 22.3739)"
      fill="#121619"
      stroke="#5685A9"
    />
    <rect
      x="18.2626"
      y="8.67944"
      width="9"
      height="9"
      transform="rotate(90 18.2626 8.67944)"
      fill="#121619"
      stroke="#5685A9"
    />
    <path
      d="M18.7415 5.5C18.7415 2.73858 16.5029 0.5 13.7415 0.5C10.98 0.5 8.74146 2.73858 8.74146 5.5"
      stroke="#5685A9"
    />
  </MimicComponent>
</template>
