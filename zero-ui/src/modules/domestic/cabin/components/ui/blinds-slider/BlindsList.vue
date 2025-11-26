<script setup lang="ts">
import { BlindsGroup } from "@/modules/domestic/types";
import BlindsControl from "./BlindsControl.vue";
import BlindsLabel from "./BlindsLabel.vue";
import BlindsSlider from "./BlindsSlider.vue";
import BlindsValue from "./BlindsValue.vue";

defineProps<{ group: BlindsGroup; editable?: boolean }>();
</script>

<template>
  <ul
    class="grid"
    :class="{
      'grid-cols-1': group.controls.length === 1,
      'grid-cols-2 gap-10 px-10': group.controls.length === 2,
    }"
  >
    <BlindsControl
      v-for="item in group.controls"
      :key="item.id"
      :control="item"
      :editable="editable"
      :class="{
        'max-md:text-5xl md:text-6xl': group.controls.length === 1,
        'max-md:text-3xl md:text-5xl': group.controls.length === 2,
      }"
    >
      <BlindsSlider />
      <BlindsValue class="mt-[1.5em]" />
      <BlindsLabel v-if="group.controls.length > 1" />
    </BlindsControl>
  </ul>
</template>
