<script setup lang="ts">
import { cn } from "@common/lib/utils";
import { reactiveOmit } from "@vueuse/core";
import { TabsTrigger, type TabsTriggerProps, useForwardProps } from "reka-ui";
import type { HTMLAttributes } from "vue";

const props = defineProps<TabsTriggerProps & { class?: HTMLAttributes["class"] }>();

const delegatedProps = reactiveOmit(props, "class");

const forwardedProps = useForwardProps(delegatedProps);
</script>

<template>
  <TabsTrigger
    v-bind="forwardedProps"
    :class="
      cn(
        'ring-offset-background focus-visible:ring-ring data-[state=active]:border-attention text-disabled-foreground data-[state=active]:text-foreground hover:text-foreground border-brand/0 font-headers inline-flex h-12 cursor-pointer items-center justify-center border-b px-4 py-1.5 text-sm font-medium whitespace-nowrap uppercase transition-all duration-300 focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50 md:h-14 md:text-base!',
        props.class,
      )
    "
  >
    <span class="inline-flex items-center justify-center truncate">
      <slot />
    </span>
  </TabsTrigger>
</template>
