<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { computed, HTMLAttributes, toRefs } from "vue";
import {
  ComponentOrientation,
  createMimicComponentContext,
  createSizeAndViewbox,
  MimicComponentBaseProps,
  MimicComponentProps,
  MimicComponentState,
  provideMimicComponentContext,
  useRotationDegrees,
} from ".";

const props = withDefaults(
  defineProps<
    MimicComponentProps & MimicComponentBaseProps & { class?: HTMLAttributes["class"] }
  >(),
  {
    orientation: ComponentOrientation.Up,
    baseOrientation: ComponentOrientation.Up,
    rotation: 0,
    state: MimicComponentState.Normal,
  },
);

const { baseOrientation, orientation, rotation, state } = toRefs(props);

const rotationDegrees = useRotationDegrees(orientation, baseOrientation, rotation);

const rotationStyle = computed(() => ({ transform: `rotate(${rotationDegrees.value}deg)` }));

const { stateColor, strokeWidth } = provideMimicComponentContext(
  createMimicComponentContext(state, rotationDegrees),
);
</script>

<template>
  <svg
    v-bind="createSizeAndViewbox(width, height)"
    xmlns="http://www.w3.org/2000/svg"
    fill="none"
    aria-hidden="true"
    :class="cn('', props.class)"
  >
    <rect
      width="100%"
      height="100%"
      fill="transparent"
    />
    <g
      :style="rotationStyle"
      class="origin-center transition-transform duration-300"
    >
      <slot
        v-bind="{
          state,
          stateColor,
          strokeWidth,
        }"
      />
    </g>
  </svg>
</template>
