<script setup lang="ts">
import type { SliderRootEmits, SliderRootProps } from "radix-vue";
import { cn } from "@/lib/utils";
import { SliderRange, SliderRoot, SliderTrack, useForwardPropsEmits } from "radix-vue";
import { computed, type HTMLAttributes } from "vue";

const props = defineProps<SliderRootProps & { class?: HTMLAttributes["class"]; steps?: number }>();
const emits = defineEmits<SliderRootEmits>();

const delegatedProps = computed(() => {
  const { class: _, ...delegated } = props;

  return delegated;
});

const forwarded = useForwardPropsEmits(delegatedProps, emits);

const positions = computed(() => (delegatedProps.value.modelValue ?? []).map(getPosition));

const getPosition = (val: number) =>
  ((val - (delegatedProps.value.min ?? 0)) /
    ((delegatedProps.value.max ?? 1) - (delegatedProps.value.min ?? 0))) *
  100;

const stepPositions = computed(() =>
  !delegatedProps.value.steps
    ? []
    : new Array(delegatedProps.value.steps - 1)
        .fill(100 / delegatedProps.value.steps)
        .map((offset, i) => offset + offset * i)
        .map(getPosition),
);
</script>

<template>
  <SliderRoot
    :class="
      cn(
        'relative flex w-full touch-none select-none items-center data-[orientation=vertical]:flex-col data-[orientation=vertical]:w-full data-[orientation=vertical]:h-full',
        props.class,
      )
    "
    v-bind="forwarded"
    :step="steps ? 100 / steps : undefined"
    orientation="vertical"
  >
    <SliderTrack
      class="relative h-1.5 w-full data-[orientation=vertical]:w-full grow overflow-hidden bg-primary/90 rounded-md"
    >
      <SliderRange class="absolute h-full data-[orientation=vertical]:w-full bg-muted/80" />
    </SliderTrack>
    <div
      v-for="step in stepPositions"
      :style="{ bottom: step + '%' }"
      class="block absolute translate-y-[65%] h-[1px] w-full bg-muted-foreground"
    ></div>
    <div
      v-for="pos in positions"
      :style="{ bottom: pos + '%' }"
      class="block absolute shadow-sm translate-y-[50%] h-3 w-[105%] -mx-[1.5%] rounded-lg cursor-pointer disabled:cursor-default border-2 border-primary bg-background ring-offset-background transition-color focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50"
    >
      <div
        class="absolute left-[50%] translate-y-[-50%] translate-x-[-50%] top-[50%] h-1 w-[20%] rounded-lg bg-primary"
      ></div>
    </div>
  </SliderRoot>
</template>
