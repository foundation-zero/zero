<script setup lang="ts">
import { cn } from "@common/lib/utils";
import { RiSubtractLine } from "@remixicon/vue";
import { reactiveOmit } from "@vueuse/core";
import type { NumberFieldDecrementProps } from "reka-ui";
import { NumberFieldDecrement, useForwardProps } from "reka-ui";
import type { HTMLAttributes } from "vue";

const props = defineProps<NumberFieldDecrementProps & { class?: HTMLAttributes["class"] }>();

const delegatedProps = reactiveOmit(props, "class");

const forwarded = useForwardProps(delegatedProps);
</script>

<template>
  <NumberFieldDecrement
    data-slot="decrement"
    v-bind="forwarded"
    :class="
      cn(
        'absolute top-1/2 left-0 -translate-y-1/2 p-3 disabled:cursor-not-allowed disabled:opacity-20',
        props.class,
      )
    "
  >
    <slot>
      <RiSubtractLine class="h-4 w-4" />
    </slot>
  </NumberFieldDecrement>
</template>
