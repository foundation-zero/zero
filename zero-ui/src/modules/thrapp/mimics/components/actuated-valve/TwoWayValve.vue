<script setup lang="ts">
import { Ratio } from "@/modules/thrs/types";
import ValvePortLeft from "./ValvePortLeft.vue";
import ValvePortRight from "./ValvePortRight.vue";

defineProps<{ flow: Ratio }>();
</script>

<template>
  <ValvePortLeft :flow="flow" />
  <ValvePortRight :flow="flow" />
</template>
