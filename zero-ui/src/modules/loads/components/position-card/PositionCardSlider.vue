<script setup lang="ts">
import { getContext } from ".";
import {
  PositionSlider,
  PositionSliderThumb,
  PositionSliderTrack,
  SliderType,
} from "../position-slider";

const props = defineProps<{
  type: SliderType;
}>();

const { state, value } = getContext();
</script>

<template>
  <PositionSlider>
    <PositionSliderTrack :type="props.type">
      <PositionSliderThumb
        :value="value"
        :state="state"
      />
    </PositionSliderTrack>
  </PositionSlider>
</template>
