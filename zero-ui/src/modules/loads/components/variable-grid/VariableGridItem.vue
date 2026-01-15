<script setup lang="ts">
import { computed } from "vue";
import { getContext } from ".";
import { useVariablesStore } from "../../stores/variables";
import { VariableUnit } from "../../types";
import MastLock from "../mast-lock/MastLock.vue";
import {
  PositionCard,
  PositionCardReferenceTarget,
  PositionCardSlider,
  PositionCardTitle,
  PositionCardValue,
} from "../position-card";
import { ReferenceBoxLine } from "../reference-box";
import {
  VariableCard,
  VariableCardReferenceTarget,
  VariableCardReferenceThresholds,
  VariableCardValue,
} from "../variable-card";
import VariableCardTitle from "../variable-card/VariableCardTitle.vue";

const props = defineProps<{ id: string }>();

const { type } = getContext();
const { getVariableById } = useVariablesStore();

const variable = computed(() => getVariableById(props.id).value);

const isNumerical = computed(
  () =>
    type.value === "numerical" ||
    variable.value?.reference?.target === undefined ||
    variable.value?.variable?.unit === VariableUnit.Tonne,
);

const isMastLock = computed(() => variable.value?.variable?.unit === VariableUnit.Bool);
const overhoist = computed(() => {
  if (isMastLock.value) {
    return getVariableById<boolean>(props.id.replace("lock", "overhoist")).value;
  }

  return undefined;
});
</script>

<template>
  <template v-if="variable">
    <MastLock
      v-if="isMastLock"
      class="col-span-1 w-full max-w-full"
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
      <VariableCardReferenceTarget>
        <ReferenceBoxLine />
      </VariableCardReferenceTarget>

      <VariableCardValue />
      <VariableCardTitle>{{ variable?.variable?.name }}</VariableCardTitle>
      <VariableCardReferenceThresholds />
    </VariableCard>
    <PositionCard
      v-else
      class="col-span-2 w-full"
      :thresholds="variable?.reference"
      :value="<number>variable.actual?.value"
    >
      <PositionCardReferenceTarget />
      <PositionCardSlider type="asymmetric" />
      <PositionCardValue />
      <PositionCardTitle>{{ variable?.variable?.name }}</PositionCardTitle>
    </PositionCard>
  </template>
</template>
