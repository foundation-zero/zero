<script setup lang="ts">
import { computed } from "vue";
import { getContext } from ".";
import { useVariablesStore } from "../../stores/variables";
import { Variable, VariableUnit } from "../../types";
import { LoadsCard, LoadsCardFooter, LoadsCardStateLabel, LoadsCardTitle } from "../loads-card";
import { MastLock } from "../mast-lock";
import { MastLockCompact } from "../mast-lock-compact";
import {
  PositionCard,
  PositionCardFooter,
  PositionCardReferenceTarget,
  PositionCardSlider,
  PositionCardStateLabel,
  PositionCardTitle,
  PositionCardValue,
} from "../position-card";
import {
  VariableCard,
  VariableCardReferenceTarget,
  VariableCardReferenceThresholds,
  VariableCardState,
  VariableCardTitle,
  VariableCardValue,
} from "../variable-card";

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
    v-if="isMastLock && type === 'graphical'"
    class="col-span-1 w-full max-w-full"
    :locked="!!variable.actual?.value"
    :overhoist="!!overhoist?.actual?.value"
  >
    {{ variable?.variable?.name }}
  </MastLock>
  <MastLockCompact
    v-else-if="isMastLock && type === 'numerical'"
    class="col-span-1 w-full max-w-full"
    :locked="!!variable.actual?.value"
    :overhoist="!!overhoist?.actual?.value"
  >
    {{ variable?.variable?.name }}
  </MastLockCompact>
  <VariableCard
    v-else-if="isNumerical"
    :thresholds="variable?.reference"
    :value="<number>variable.actual?.value"
    :type="variable?.variable?.unit"
    class="col-span-1 w-full max-w-full"
  >
    <VariableCardTitle>{{ variable?.variable?.name }}</VariableCardTitle>
    <div class="flex w-full flex-nowrap items-baseline-last whitespace-nowrap">
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
    class="col-span-1 w-full max-w-full"
  >
    <LoadsCardFooter>
      <LoadsCardStateLabel class="w-1/5 text-center">{{
        variable?.variable.scaleMinLabel
      }}</LoadsCardStateLabel>
      <LoadsCardTitle class="justify-center">{{ variable?.variable?.name }}</LoadsCardTitle>
      <LoadsCardStateLabel class="w-1/5 text-center">{{
        variable?.variable.scaleMaxLabel
      }}</LoadsCardStateLabel>
    </LoadsCardFooter>
  </LoadsCard>
  <PositionCard
    v-else
    class="col-span-1 w-full"
    :thresholds="variable?.reference"
    :value="<number>variable.actual?.value"
  >
    <PositionCardReferenceTarget />
    <PositionCardSlider :type="variable.variable.scaleMin < 0 ? 'symmetric' : 'asymmetric'" />
    <PositionCardValue />
    <PositionCardFooter>
      <PositionCardStateLabel class="w-1/5 text-center">{{
        variable?.variable.scaleMinLabel
      }}</PositionCardStateLabel>
      <PositionCardTitle class="justify-center">{{ variable?.variable?.name }}</PositionCardTitle>
      <PositionCardStateLabel class="w-1/5 text-center">{{
        variable?.variable.scaleMaxLabel
      }}</PositionCardStateLabel>
    </PositionCardFooter>
  </PositionCard>
</template>
