<script setup lang="ts">
import { cn } from "@/lib/utils";
import { TabsList, type TabsListProps } from "radix-vue";
import { computed, type HTMLAttributes } from "vue";

const props = defineProps<TabsListProps & { class?: HTMLAttributes["class"] }>();

const delegatedProps = computed(() => {
  const { class: _, ...delegated } = props;

  return delegated;
});
</script>

<template>
  <TabsList
    v-bind="delegatedProps"
    :class="cn('flex w-full items-center justify-evenly py-2 text-muted-foreground', props.class)"
  >
    <slot />
  </TabsList>
</template>
