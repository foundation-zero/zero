<script setup lang="ts">
import { DC_CONVERTER_HEIGHT, DC_CONVERTER_WIDTH } from ".";
import { MimicComponentBaseProps } from "..";
import { Pvt } from "../pvt";

withDefaults(defineProps<MimicComponentBaseProps & { width?: number; height?: number }>(), {
  width: () => DC_CONVERTER_WIDTH,
  height: () => DC_CONVERTER_HEIGHT,
});
</script>

<template>
  <Pvt
    :width="width"
    :height="height"
    force-height
    :state="state"
    class="p-4"
  >
    <slot />
  </Pvt>
</template>
