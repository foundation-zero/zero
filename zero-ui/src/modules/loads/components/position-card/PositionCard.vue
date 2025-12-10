<script setup lang="ts">
import { computed, toRefs } from "vue";
import { provideContext } from ".";
import { getLoadState } from "../../lib/utils";
import { ReferenceThresholds, VariableType } from "../../types";
import Card from "../card/Card.vue";
import { SliderType } from "../position-slider";
import ReferenceBox from "../reference-box/ReferenceBox.vue";
import ReferenceBoxValue from "../reference-box/ReferenceBoxValue.vue";
import { VariableState as VariableStateDisplay, VariableUnit } from "../variable-state";
import PositionCardSlider from "./PositionCardSlider.vue";

const props = defineProps<{
  value: number;
  thresholds?: ReferenceThresholds;
  type: SliderType;
}>();

const { value, thresholds } = toRefs(props);

const state = computed(() => getLoadState(value.value, props.thresholds));

provideContext({
  value,
  state,
  thresholds,
});
</script>

<template>
  <Card class="w-full max-w-[21rem] gap-3">
    <ReferenceBox
      class="-mt-1"
      :class="{ invisible: !thresholds?.target }"
    >
      <ReferenceBoxValue
        :value="thresholds?.target"
        :type="VariableType.Percentage"
      />
    </ReferenceBox>

    <PositionCardSlider :type="type" />

    <div class="flex w-full flex-col items-center">
      <VariableStateDisplay
        :type="VariableType.Percentage"
        size="xl"
        :value="value"
        :state="state"
      >
        <VariableUnit />
      </VariableStateDisplay>

      <div
        class="text-disabled-foreground flex items-center gap-1 py-2 text-base font-medium text-ellipsis"
      >
        <slot />
      </div>
    </div>
  </Card>
</template>
