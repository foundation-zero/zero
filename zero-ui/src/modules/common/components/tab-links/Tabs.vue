<script setup lang="ts" generic="T extends string | number">
import { cn } from "@common/lib/utils";
import { reactiveOmit } from "@vueuse/core";
import type { TabsRootEmits, TabsRootProps } from "reka-ui";
import { TabsRoot, useForwardPropsEmits } from "reka-ui";
import type { HTMLAttributes } from "vue";

const props = defineProps<TabsRootProps<T> & { class?: HTMLAttributes["class"] }>();
const emits = defineEmits<TabsRootEmits<T>>();

const delegatedProps = reactiveOmit(props, "class");
const forwarded = useForwardPropsEmits(delegatedProps, emits);
</script>

<template>
  <TabsRoot
    data-slot="tabs"
    v-bind="forwarded"
    :class="cn('flex flex-col gap-2', props.class)"
  >
    <slot />
  </TabsRoot>
</template>
