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
    :class="cn('text-muted-foreground flex w-full items-center justify-evenly py-2', props.class)"
  >
    <slot />
  </TabsList>
</template>
