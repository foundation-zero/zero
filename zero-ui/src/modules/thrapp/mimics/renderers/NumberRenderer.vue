<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import AnimatedNumber from "@/modules/loads/components/animated-number/AnimatedNumber.vue";
import { computed } from "vue";
import { getFieldValue } from "../providers/index.ts";
import { FieldRendererProps } from "./index.ts";

const props = defineProps<
  FieldRendererProps<number> & {
    unit?: string | ((val: number) => string);
    dense?: boolean;
    transform?: (value: number) => number;
  }
>();

const fieldValue = getFieldValue<number>();
const value = computed(() => {
  const rawValue = props.value !== undefined ? props.value : fieldValue.value;
  return props.transform && rawValue !== undefined ? props.transform(rawValue) : rawValue;
});

const unit = computed(() => {
  if (typeof props.unit === "function") {
    return value.value !== undefined ? props.unit(value.value) : undefined;
  }

  return props.unit;
});
</script>

<template>
  <span
    data-slot="field-value"
    :class="cn('inline-flex items-center', { 'gap-0.5': !dense }, props.class)"
  >
    <AnimatedNumber
      :to="value"
      :format="format"
    />
    <span v-if="unit">{{ unit }}</span>
  </span>
</template>
