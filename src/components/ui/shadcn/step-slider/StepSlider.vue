<script setup lang="ts">
import { cn } from "@/lib/utils";
import type { SliderRootEmits, SliderRootProps } from "radix-vue";
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
        'relative flex w-full touch-none select-none items-center disabled:pointer-events-none disabled:cursor-not-allowed disabled:opacity-50 data-[orientation=vertical]:h-full data-[orientation=vertical]:w-full data-[orientation=vertical]:flex-col',
        props.class,
      )
    "
    v-bind="forwarded"
    :step="steps ? 100 / steps : undefined"
    orientation="vertical"
  >
    <SliderTrack
      class="relative h-1.5 w-full grow overflow-hidden rounded-md bg-primary/90 data-[orientation=vertical]:w-full"
    >
      <SliderRange
        class="absolute h-full rounded-md bg-muted/80 data-[orientation=vertical]:w-full"
      />
    </SliderTrack>
    <div
      v-for="step in stepPositions"
      :key="step"
      :style="{ bottom: step + '%' }"
      class="absolute block h-[1px] w-full translate-y-[65%] bg-muted-foreground"
    ></div>
    <div
      v-for="pos in positions"
      :key="pos"
      :style="{ bottom: pos + '%' }"
      class="transition-color absolute -mx-[1.5%] block h-3 w-[105%] translate-y-[50%] cursor-pointer rounded-lg border-2 border-primary bg-background shadow-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:cursor-default disabled:opacity-50"
    >
      <div
        class="absolute left-[50%] top-[50%] h-1 w-[20%] translate-x-[-50%] translate-y-[-50%] rounded-lg bg-primary"
      ></div>
    </div>
  </SliderRoot>
</template>
