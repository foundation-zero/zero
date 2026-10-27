<script setup lang="ts" generic="T">
import type { toggleVariants } from "@/components/ui/toggle";
import { cn } from "@common/lib/utils";
import { reactiveOmit } from "@vueuse/core";
import type { VariantProps } from "class-variance-authority";
import type { AcceptableValue, ToggleGroupRootProps } from "reka-ui";
import { ToggleGroupRoot, useForwardProps } from "reka-ui";
import type { HTMLAttributes } from "vue";
import { provide } from "vue";

type ToggleGroupVariants = VariantProps<typeof toggleVariants>;

const props = defineProps<
  ToggleGroupRootProps<T> & {
    class?: HTMLAttributes["class"];
    variant?: ToggleGroupVariants["variant"];
    size?: ToggleGroupVariants["size"];
  }
>();

type ToggleGroupRootEmits<T> = {
  /** Event handler called when the value changes. */
  "update:modelValue": [payload: T];
};

const emits = defineEmits<ToggleGroupRootEmits<T>>();

provide("toggleGroup", {
  variant: props.variant,
  size: props.size,
});

const delegatedProps = reactiveOmit(props, "class");

const forwarded = useForwardProps(delegatedProps);

// reka-ui emits untyped values; narrow them to the type the caller bound to `modelValue`
const onUpdate = (value: AcceptableValue | AcceptableValue[]) =>
  emits("update:modelValue", value as T);
</script>

<template>
  <ToggleGroupRoot
    v-slot="slotProps"
    v-bind="forwarded"
    :class="cn('flex items-center justify-center gap-1', props.class)"
    @update:model-value="onUpdate"
  >
    <slot v-bind="slotProps" />
  </ToggleGroupRoot>
</template>
