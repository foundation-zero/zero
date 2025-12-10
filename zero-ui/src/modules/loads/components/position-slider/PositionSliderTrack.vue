<script setup lang="ts">
import { computed, toRefs } from "vue";
import { provideTrackContext, SliderType } from ".";

const props = defineProps<{
  type: SliderType;
}>();

const { type } = toRefs(props);

// Values from -100 to 100 for symmetric, 0 to 100 for asymmetric
const SYMMETRIC_VALUES = new Array(21).fill(0).map((_, index) => index * 10 - 100);
const ASYMMETRIC_VALUES = new Array(21).fill(0).map((_, index) => index * 5);

const trackValues = computed(() =>
  props.type === "symmetric" ? SYMMETRIC_VALUES : ASYMMETRIC_VALUES,
);

provideTrackContext({ type });
</script>

<template>
  <div
    data-slot="position-slider-track"
    class="relative flex h-full w-full items-center justify-between"
  >
    <div
      v-for="(value, index) in trackValues"
      :key="value"
      data-slot="position-slider-track-value"
      class="border-border-subtle text-3xs relative w-0 border-l"
      :data-value="value"
      :class="{
        'text-attention': value === 0,
        'text-muted-foreground': value !== 0,
        'text-sm': Math.abs(value) % 100 === 0,
        'h-3/4': index % 2 === 0,
        'h-1/2': index % 2 !== 0,
      }"
    />

    <slot />
  </div>
</template>

<style lang="scss" scoped>
[data-slot="position-slider-track-value"] {
  &:nth-child(even) {
    &:after {
      display: none;
    }
  }

  &:after {
    content: attr(data-value);
    position: absolute;
    bottom: -33.3333%;
    line-height: 0.875rem;
    transform: translateX(-50%) translateY(100%);
    white-space: nowrap;
  }
}
</style>
