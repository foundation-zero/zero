<script setup lang="ts">
import { cn } from "@/lib/utils";
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
        'ring-offset-background focus-visible:ring-ring data-[state=active]:bg-brand data-[state=active]:text-button-foreground inline-flex cursor-pointer items-center justify-center rounded-full px-4 py-1.5 text-sm font-normal whitespace-nowrap transition-all focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none disabled:pointer-events-none disabled:opacity-50 data-[state=active]:shadow md:text-base',
        props.class,
      )
    "
  >
    <span class="inline-flex items-center justify-center truncate">
      <slot />
    </span>
  </TabsTrigger>
</template>
