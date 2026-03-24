<script setup lang="ts">
import { cn, mmath } from "@/modules/common/lib/utils";
import { computed, HTMLAttributes } from "vue";
import { getContext } from ".";
import { Nullable } from "../../types";

const props = defineProps<{
  class?: HTMLAttributes["class"];
  min: Nullable<number>;
  max: Nullable<number>;
  minLabel: Nullable<string>;
  maxLabel: Nullable<string>;
}>();

const { value } = getContext();

const label = computed(() => {
  if (
    value.value == null ||
    props.min == null ||
    props.max == null ||
    props.minLabel == null ||
    props.maxLabel == null
  )
    return null;

  // For asymmetric scales we always show the minLabel
  if (props.min === 0) return props.minLabel;

  // For symmetric scales we show the label based on which side of the threshold the value is
  const threshold = mmath.avg(props.min, props.max);

  if (value.value < threshold) {
    return props.minLabel;
  } else {
    return props.maxLabel;
  }
});
</script>

<template>
  <span
    v-if="label"
    class="text-muted-foreground ml-1 text-sm"
    :class="cn(props.class)"
  >
    {{ label }}
  </span>
</template>
