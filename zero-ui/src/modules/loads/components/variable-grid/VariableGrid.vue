<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { toRefs } from "vue";
import { provideContext, toGridSize } from ".";
import { CardType } from "../../types";

const props = defineProps<{ type: CardType }>();

provideContext(toRefs(props));
</script>

<template>
  <div :class="cn('grid gap-3 lg:gap-4', toGridSize(type))">
    <slot />
  </div>
</template>
