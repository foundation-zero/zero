<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes, toRefs } from "vue";
import {
  ComponentOrientation,
  createMimicComponentContext,
  createSizeAndViewbox,
  MimicComponentBaseProps,
  MimicComponentProps,
  MimicComponentState,
  provideMimicComponentContext,
  useOrientation,
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

const rotationStyle = useOrientation(orientation, baseOrientation, rotation);

const { stateColor, strokeWidth } = provideMimicComponentContext(
  createMimicComponentContext(state),
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
