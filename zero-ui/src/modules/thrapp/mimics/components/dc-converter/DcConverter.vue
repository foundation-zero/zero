<script setup lang="ts">
import { MimicComponentBaseProps } from "..";
import { Pvt } from "../pvt";

withDefaults(defineProps<MimicComponentBaseProps & { width?: number; height?: number }>(), {
  width: 200,
  height: 205,
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
