<script setup lang="ts">
import { useIntervalFn, useRafFn } from "@vueuse/core";
import { isEqual } from "lodash";
import { computed, ref, watch } from "vue";
import { Colors, getGaugeRootContext } from ".";
import GaugePoint from "./GaugePoint.vue";

const enum Direction {
  Clockwise = "clockwise",
  CounterClockwise = "counter-clockwise",
  None = "none",
}

const props = withDefaults(
  defineProps<{
    animationDuration?: number;
  }>(),
  {
    animationDuration: 300,
  },
);

const { points, currentValue, target } = getGaugeRootContext();

const states = computed(() => points.value.map(({ color }) => color));

// For the first render, we want to start with the initial states to avoid animation glitches
const animatedStates = ref<Colors[]>(states.value);
let animationDirection = Direction.None;

const getNextIndex = () => {
  if (animationDirection === Direction.Clockwise) {
    return animatedStates.value.findIndex((state, i) => state !== states.value[i]);
  } else if (animationDirection === Direction.CounterClockwise) {
    return animatedStates.value.findLastIndex((state, i) => state !== states.value[i]);
  }
  return null;
};

const animationTimer = useIntervalFn(() => {
  if (isEqual(states.value, animatedStates.value)) {
    animationTimer.pause();
    return;
  }

  const newAnimatedStates = [...animatedStates.value];
  const index = getNextIndex();

  if (index !== null) {
    useRafFn(
      () => {
        newAnimatedStates[index] = states.value[index];
        animatedStates.value = newAnimatedStates;
      },
      { once: true },
    );
  }
}, props.animationDuration! / points.value.length);

watch(
  () => currentValue?.value,
  (next, prev) => {
    if (next === undefined) return;

    const previousValue = prev === undefined ? target.value : prev;

    if (next === previousValue) {
      return;
    } else if (next > previousValue) {
      animationDirection = Direction.Clockwise;
    } else if (next < previousValue) {
      animationDirection = Direction.CounterClockwise;
    }

    animationTimer.resume();
  },
  { immediate: true },
);
</script>

<template>
  <GaugePoint
    v-for="(point, index) in points"
    :key="index"
    :cx="point.x"
    :cy="point.y"
    :fill="animatedStates[index]"
    :data-value="point.value"
  />
</template>
