<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import AnimatedNumber from "@/modules/loads/components/animated-number/AnimatedNumber.vue";
import { computed } from "vue";
import { getFieldValue } from "../providers/index.ts";
import { FieldRendererProps } from "./index.ts";

const props = defineProps<
  FieldRendererProps<number> & {
    unit?: string | ((absRawValue: number, absTransformedValue: number) => string);
    dense?: boolean;
    transform?: (value: number) => number;
  }
>();

const fieldValue = getFieldValue<number>();
const rawValue = computed(() => (props.value !== undefined ? props.value : fieldValue.value));
const transformedValue = computed(() => {
  return props.transform && rawValue.value !== undefined
    ? props.transform(rawValue.value)
    : rawValue.value;
});

const unit = computed(() => {
  if (typeof props.unit === "function") {
    return transformedValue.value !== undefined && rawValue.value !== undefined
      ? props.unit(Math.abs(rawValue.value), Math.abs(transformedValue.value))
      : undefined;
  } else {
    return props.unit;
  }
});
</script>

<template>
  <span
    data-slot="field-value"
    :class="cn('inline-flex items-center', { 'gap-0.5': !dense }, props.class)"
  >
    <AnimatedNumber
      :to="transformedValue"
      :format="format"
    />
    <span v-if="unit">{{ unit }}</span>
  </span>
</template>
