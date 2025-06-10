<script setup lang="ts">
import { cn } from "@/lib/utils";
import { Minus } from "lucide-vue-next";
import type { NumberFieldDecrementProps } from "radix-vue";
import { NumberFieldDecrement, useForwardProps } from "radix-vue";
import type { HTMLAttributes } from "vue";
import { computed } from "vue";

const props = defineProps<NumberFieldDecrementProps & { class?: HTMLAttributes["class"] }>();

const delegatedProps = computed(() => {
  const { class: _, ...delegated } = props;

  return delegated;
});

const forwarded = useForwardProps(delegatedProps);
</script>

<template>
  <NumberFieldDecrement
    data-slot="decrement"
    v-bind="forwarded"
    :class="
      cn(
        'absolute left-0 top-1/2 -translate-y-1/2 p-3 disabled:cursor-not-allowed disabled:opacity-20',
        props.class,
      )
    "
  >
    <slot>
      <Minus class="h-7 w-7" />
    </slot>
  </NumberFieldDecrement>
</template>
