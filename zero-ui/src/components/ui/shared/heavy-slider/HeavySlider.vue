<script setup lang="ts">
import { cn } from "@/lib/utils";
import type { SliderRootEmits, SliderRootProps } from "radix-vue";
import { SliderRange, SliderRoot, SliderTrack, useForwardPropsEmits } from "radix-vue";
import { computed, type HTMLAttributes } from "vue";

const props = defineProps<SliderRootProps & { class?: HTMLAttributes["class"] }>();
const emits = defineEmits<SliderRootEmits>();

const delegatedProps = computed(() => {
  const { class: _, ...delegated } = props;

  return delegated;
});

const forwarded = useForwardPropsEmits(delegatedProps, emits);

const positions = computed(() =>
  (delegatedProps.value.modelValue ?? []).map(
    (val) =>
      ((val - (delegatedProps.value.min ?? 0)) /
        ((delegatedProps.value.max ?? 1) - (delegatedProps.value.min ?? 0))) *
      100,
  ),
);
</script>

<template>
  <SliderRoot
    :class="
      cn(
        'relative flex w-full touch-none select-none items-center data-[orientation=vertical]:h-full data-[orientation=vertical]:w-full data-[orientation=vertical]:flex-col',
        props.class,
      )
    "
    v-bind="forwarded"
    orientation="vertical"
  >
    <SliderTrack
      class="relative h-1.5 w-full grow overflow-hidden rounded-3xl bg-primary/10 data-[orientation=vertical]:w-full"
    >
      <SliderRange class="absolute h-full bg-primary/90 data-[orientation=vertical]:w-full" />
    </SliderTrack>
    <div
      v-for="pos in positions"
      :key="pos"
      :style="{ bottom: pos + '%' }"
      class="transition-color absolute block h-3 w-10 translate-y-[65%] cursor-pointer rounded-full border-2 border-primary/90 bg-background ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:cursor-default disabled:opacity-50"
    />
  </SliderRoot>
</template>
