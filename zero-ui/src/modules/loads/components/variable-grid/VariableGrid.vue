<script setup lang="ts">
import { toRefs } from "vue";
import { provideContext } from ".";
import { CardType } from "../../types";

const props = defineProps<{ type: CardType }>();

provideContext(toRefs(props));
</script>

<template>
  <div
    class="3xl:grid-cols-10 4xl:grid-cols-12 grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 lg:gap-4 xl:grid-cols-6 2xl:grid-cols-8"
  >
    <slot />
  </div>
</template>
