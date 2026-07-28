<script setup lang="ts">
import { Ratio } from "@/modules/thrsim/types/index.ts";
import ValvePortBottom from "./ValvePortBottom.vue";
import ValvePortLeft from "./ValvePortLeft.vue";
import ValvePortRight from "./ValvePortRight.vue";

defineProps<{ flow: Ratio }>();
</script>

<template>
  <ValvePortLeft :flow="flow" />
  <ValvePortRight :flow="1" />
  <ValvePortBottom :flow="1 - flow" />
</template>
