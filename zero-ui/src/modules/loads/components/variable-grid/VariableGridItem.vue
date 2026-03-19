<script setup lang="ts">
import { computed } from "vue";
import { getContext } from ".";
import { useVariablesStore } from "../../stores/variables";
import { Variable, VariableUnit } from "../../types";
import LoadsCard from "../loads-card/LoadsCard.vue";
import MastLock from "../mast-lock/MastLock.vue";
import {
  PositionCard,
  PositionCardReferenceTarget,
  PositionCardSlider,
  PositionCardTitle,
  PositionCardValue,
} from "../position-card";
import { VariableCard, VariableCardReferenceThresholds, VariableCardValue } from "../variable-card";
import VariableCardReferenceTarget from "../variable-card/VariableCardReferenceTarget.vue";
import VariableCardState from "../variable-card/VariableCardState.vue";
import VariableCardTitle from "../variable-card/VariableCardTitle.vue";

const props = defineProps<{ id: string; variable: Variable }>();

const { type } = getContext();
const { getVariableById } = useVariablesStore();

const isNumerical = computed(
  () =>
    type.value === "numerical" ||
    props.variable.variable.scaleMin === undefined ||
    props.variable.variable.scaleMax === undefined,
);

const isMastLock = computed(() => props.variable.variable?.unit === VariableUnit.Bool);
const isLoad = computed(() => props.variable.variable?.unit === VariableUnit.Tonne);
const overhoist = computed(() => {
  if (isMastLock.value) {
    return getVariableById<boolean>(props.id.replace("lock", "overhoist")).value;
  }

  return undefined;
});
</script>

<template>
  <MastLock
    v-if="isMastLock"
    class="col-span-2 w-full max-w-full"
    :locked="!!variable.actual?.value"
    :overhoist="!!overhoist?.actual?.value"
  >
    {{ variable?.variable?.name }}
  </MastLock>
  <VariableCard
    v-else-if="isNumerical"
    :thresholds="variable?.reference"
    :value="<number>variable.actual?.value"
    :type="variable?.variable?.unit"
    class="col-span-1 w-full max-w-full"
  >
    <VariableCardTitle>{{ variable?.variable?.name }}</VariableCardTitle>
    <div class="w-full">
      <VariableCardValue />
      <VariableCardState
        :min="variable?.variable.scaleMin"
        :max="variable?.variable.scaleMax"
        :min-label="variable?.variable.scaleMinLabel"
        :max-label="variable?.variable.scaleMaxLabel"
      />
    </div>
    <hr class="w-full" />
    <VariableCardReferenceThresholds>
      <VariableCardReferenceTarget />
    </VariableCardReferenceThresholds>
  </VariableCard>
  <LoadsCard
    v-else-if="isLoad"
    :thresholds="variable?.reference"
    :value="<number>variable.actual?.value"
    :scale="[variable.variable.scaleMin, variable.variable.scaleMax]"
    class="col-span-2 w-full max-w-full"
  >
    <VariableCardTitle class="-mt-2 w-full justify-center">{{
      variable?.variable?.name
    }}</VariableCardTitle>
  </LoadsCard>
  <PositionCard
    v-else
    class="col-span-2 w-full"
    :thresholds="variable?.reference"
    :value="<number>variable.actual?.value"
  >
    <PositionCardReferenceTarget />
    <PositionCardSlider :type="variable.variable.scaleMin < 0 ? 'symmetric' : 'asymmetric'" />
    <PositionCardValue />
    <PositionCardTitle class="w-full justify-center">{{
      variable?.variable?.name
    }}</PositionCardTitle>
  </PositionCard>
</template>
