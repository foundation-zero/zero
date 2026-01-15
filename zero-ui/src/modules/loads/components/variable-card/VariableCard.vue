<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { computed, HTMLAttributes, toRefs } from "vue";
import { provideContext } from ".";
import { getLoadState } from "../../lib/utils";
import { ReferenceThresholds, VariableUnit } from "../../types";
import { Card } from "../card";

const props = defineProps<{
  value: number;
  thresholds?: Partial<ReferenceThresholds>;
  type: VariableUnit;
  class?: HTMLAttributes["class"];
}>();

const { value, thresholds, type } = toRefs(props);

const state = computed(() => getLoadState(props.value, props.thresholds));

provideContext({
  state,
  value,
  thresholds,
  type,
});
</script>

<template>
  <Card
    data-slot="card"
    :class="cn('h-[13.375rem] min-w-[11em] gap-2', state, props.class)"
  >
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
