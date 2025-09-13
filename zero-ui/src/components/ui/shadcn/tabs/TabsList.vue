<script setup lang="ts">
import { cn } from "@/lib/utils";
import { reactiveOmit } from "@vueuse/core";
import { TabsList, type TabsListProps } from "reka-ui";
import type { HTMLAttributes } from "vue";

const props = defineProps<TabsListProps & { class?: HTMLAttributes["class"] }>();

const delegatedProps = reactiveOmit(props, "class");
</script>

<template>
  <TabsList
    v-bind="delegatedProps"
    :class="
      cn('text-primary inline-flex items-center justify-center rounded-full p-1', props.class)
    "
  >
    <slot />
  </TabsList>
</template>
