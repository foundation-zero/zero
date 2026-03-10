<template>
  <component
    :is="tag ?? 'span'"
    v-if="to === undefined"
  >
    -
  </component>
  <AnimatedNumber
    v-else-if="isBrowser"
    :from="0"
    :format="formatNumber(1)"
    :to="to"
    :tag="tag"
  />
</template>

<script setup lang="ts">
import { formatNumber } from "@/modules/common/lib/utils";
import AnimatedNumber from "vue-number-animation";

// Without this check building the vitepress docs will fail.
const isBrowser = typeof window !== "undefined" && typeof window.document !== "undefined";

defineProps<{ to?: number; tag?: string }>();
</script>
