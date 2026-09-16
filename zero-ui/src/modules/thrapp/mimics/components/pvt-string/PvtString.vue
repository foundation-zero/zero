<script setup lang="ts">
import { PVT_BASE_ORIENTATION, PVT_STRING_HEIGHT, PVT_STRING_WIDTH, PvtStringProps } from ".";
import { MimicComponentBaseProps, MimicComponentState } from "..";
import MimicComponent from "../MimicComponent.vue";
import PvtStringElement from "./PvtStringElement.vue";

const props = withDefaults(defineProps<MimicComponentBaseProps & PvtStringProps>(), {
  state: MimicComponentState.Normal,
  orientation: PVT_BASE_ORIENTATION,
  width: PVT_STRING_WIDTH,
  height: PVT_STRING_HEIGHT,
});
</script>

<template>
  <MimicComponent
    :width="props.width"
    :height="props.height"
    :viewBox="`0 0 ${PVT_STRING_WIDTH} ${PVT_STRING_HEIGHT}`"
    :base-orientation="PVT_BASE_ORIENTATION"
    :orientation="orientation"
    :state="state"
    data-slot="pvt-string"
  >
    <PvtStringElement />
    <text>
      <tspan
        class="fill-muted-foreground text-xs"
        x="28"
        text-anchor="end"
        stroke-width="1"
        y="10.75"
      >
        <slot />
      </tspan>
    </text>
  </MimicComponent>
</template>
