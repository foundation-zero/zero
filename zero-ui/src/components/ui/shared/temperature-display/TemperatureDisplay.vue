<script setup lang="ts">
import { separateDecimals } from "@/lib/utils";
import { toRef } from "vue";

const props = defineProps<{ value: number }>();
const value = toRef(props, "value");

const { integer, decimal } = separateDecimals(value);
</script>

<template>
  <span class="relative">
    <span class="font-headers font-bold uppercase">
      {{ integer }}
    </span>
    <span class="font-headers text-r3xs ml-[0.15em] font-light">
      {{ decimal }}
    </span>
    <span class="font-headers text-rxs absolute top-[-0.10em] right-[0.05em] pt-1 font-thin">
      &deg;
    </span>
  </span>
</template>
