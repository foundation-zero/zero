<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import AnimatedNumber from "@/modules/loads/components/animated-number/AnimatedNumber.vue";
import { toRef } from "vue";
import { getFieldValue } from "../providers/index.ts";
import { FieldRendererProps } from "./index.ts";

const props = defineProps<
  FieldRendererProps<number> & {
    unit?: string;
    dense?: boolean;
  }
>();

const value = getFieldValue(toRef(props, "value"));
</script>

<template>
  <span
    data-slot="field-value"
    :class="cn('flex items-center', props.class)"
  >
    <AnimatedNumber
      :to="value"
      :format="format"
    />
    <span
      v-if="unit"
      :class="{ 'pl-0.5': !dense }"
      >{{ unit }}</span
    >
  </span>
</template>
