<script setup lang="ts">
import { HTMLAttributes } from "vue";
import { getContext } from ".";
import {
  PositionSlider,
  PositionSliderThumb,
  PositionSliderTrack,
  SliderType,
} from "../position-slider";

const props = defineProps<{
  type: SliderType;
  class?: HTMLAttributes["class"];
}>();

const { state, value } = getContext();
</script>

<template>
  <PositionSlider :class="props.class">
    <PositionSliderTrack :type="props.type">
      <PositionSliderThumb
        :value="value"
        :state="state"
      />
    </PositionSliderTrack>
  </PositionSlider>
</template>
