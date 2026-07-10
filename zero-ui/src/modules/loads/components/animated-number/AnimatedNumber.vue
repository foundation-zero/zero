<template>
  <component
    :is="tag"
    v-if="to == undefined"
  >
    {{ fallback }}
  </component>
  <AnimatedNumber
    v-else-if="isBrowser"
    :from="from"
    :format="format ?? formatNumber(fractionDigits)"
    :to="to"
    :tag="tag"
  />
</template>

<script setup lang="ts">
import { formatNumber, NumberFormatter } from "@/modules/common/lib/utils";
import AnimatedNumber from "vue-number-animation";

// Without this check building the vitepress docs will fail.
const isBrowser = typeof window !== "undefined" && typeof window.document !== "undefined";

withDefaults(
  defineProps<{
    from?: number;
    to?: number | null;
    tag?: string;
    fractionDigits?: number;
    format?: NumberFormatter;
    fallback?: string;
  }>(),
  {
    from: 0,
    fractionDigits: 1,
    fallback: "-",
    tag: "span",
  },
);
</script>
