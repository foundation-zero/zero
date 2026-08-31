<template>
  <component
    :is="tag"
    v-if="to == undefined || !animate"
  >
    <template v-if="to != undefined">
      {{ format ? format(to) : formatNumber(fractionDigits)(to) }}
    </template>
    <template v-else>
      {{ fallback }}
    </template>
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
import { ENV } from "@/settings";
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
    animate?: boolean;
  }>(),
  {
    from: 0,
    fractionDigits: 1,
    fallback: "-",
    tag: "span",
    animate: ENV.VITE_ANIMATE_NUMBERS === "1" || ENV.VITE_ANIMATE_NUMBERS === "true",
  },
);
</script>
