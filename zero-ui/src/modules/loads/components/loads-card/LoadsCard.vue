<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { computed, HTMLAttributes } from "vue";
import { getLoadState } from "../../lib/utils";
import { ReferenceThresholds, VariableUnit } from "../../types";
import { Card } from "../card";
import { Gauge, GaugeTarget, Range } from "../loads-gauge";
import { ReferenceBoxLine } from "../reference-box";
import {
  VariableState as VariableStateDisplay,
  VariableUnit as VariableUnitDisplay,
} from "../variable-state";

const props = defineProps<{
  value?: number;
  thresholds?: ReferenceThresholds;
  scale: Range;
  class?: HTMLAttributes["class"];
}>();

const state = computed(() => getLoadState(props.value, props.thresholds));
</script>

<template>
  <Card
    data-slot="card"
    :class="
      cn(
        'relative h-[13.375rem] min-w-[11em] gap-2 transition-all duration-500',
        state,
        props.class,
      )
    "
  >
    <GaugeTarget
      :target="thresholds?.target"
      :class="{ invisible: thresholds?.target === undefined }"
      class="-mb-7"
    >
      <ReferenceBoxLine />
    </GaugeTarget>
    <Gauge
      :current-value="value"
      :scale="scale"
      :thresholds="thresholds"
    />

    <VariableStateDisplay
      :type="VariableUnit.Tonne"
      size="xl"
      :value="value"
      :state="state"
      class="absolute bottom-1/5"
    >
      <VariableUnitDisplay />
    </VariableStateDisplay>
    <slot />
  </Card>
</template>

<style lang="scss" scoped>
[data-slot="card"] {
  &.alarm {
    background:
      linear-gradient(
        180deg,
        oklch(from var(--color-destructive) l c h / 0),
        oklch(from var(--color-destructive) l c h / 0.1) 100%
      ),
      var(--color-background);
  }

  &.warning {
    background:
      linear-gradient(
        180deg,
        oklch(from var(--color-warning) l c h / 0),
        oklch(from var(--color-warning) l c h / 0.1) 100%
      ),
      var(--color-background);
  }
}
</style>
