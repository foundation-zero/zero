<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import AnimatedNumber from "@/modules/loads/components/animated-number/AnimatedNumber.vue";
import { computed } from "vue";
import { getFieldValue } from "../providers/index.ts";
import { FieldRendererProps } from "./index.ts";

const props = defineProps<
  FieldRendererProps<number> & {
    unit?: string;
    dense?: boolean;
  }
>();

const fieldValue = getFieldValue<number>();
const value = computed(() => (props.value !== undefined ? props.value : fieldValue.value));
</script>

<template>
  <span
    data-slot="field-value"
    :class="cn('flex items-center', { 'gap-0.5': !dense }, props.class)"
  >
    <AnimatedNumber
      :to="value"
      :format="format"
    />
    <span v-if="unit">{{ unit }}</span>
  </span>
</template>
