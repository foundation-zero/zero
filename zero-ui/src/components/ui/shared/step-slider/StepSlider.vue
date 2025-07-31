<script setup lang="ts">
import { cn } from "@/lib/utils";
import type { SliderRootEmits, SliderRootProps } from "reka-ui";
import { SliderRange, SliderRoot, SliderThumb, SliderTrack, useForwardPropsEmits } from "reka-ui";
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
    data-slot="slider"
    :class="
      cn(
        'relative flex w-full touch-none items-center select-none disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 data-[orientation=vertical]:h-full data-[orientation=vertical]:w-full data-[orientation=vertical]:flex-col',
        props.class,
      )
    "
    v-bind="forwarded"
    :step="steps ? 100 / steps : undefined"
    orientation="vertical"
  >
    <SliderTrack
      data-slot="slider-track"
      class="bg-primary/90 relative h-1.5 w-full grow overflow-hidden rounded data-[orientation=vertical]:w-full"
    >
      <SliderRange
        data-slot="slider-range"
        class="bg-muted/80 absolute h-full rounded data-[orientation=vertical]:w-full"
      />
    </SliderTrack>
    <div
      v-for="step in stepPositions"
      :key="step"
      :style="{ bottom: step + '%' }"
      class="bg-muted-foreground absolute block h-px w-full translate-y-[65%]"
    ></div>
    <SliderThumb
      v-for="pos in positions"
      :key="pos"
      :style="{ bottom: pos + '%' }"
      class="transition-color border-primary bg-background ring-offset-background focus-visible:ring-ring absolute -mx-[1.5%] block h-3 w-[105%] translate-y-[50%] cursor-pointer rounded-md border-2 shadow-sm focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none disabled:pointer-events-none disabled:cursor-default disabled:opacity-50"
    >
      <div
        class="bg-primary absolute top-[50%] left-[50%] h-1 w-[20%] translate-x-[-50%] translate-y-[-50%] rounded-md"
      ></div>
    </SliderThumb>
  </SliderRoot>
</template>
