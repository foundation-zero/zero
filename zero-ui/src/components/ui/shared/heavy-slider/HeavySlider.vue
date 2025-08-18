<script setup lang="ts">
import { cn } from "@/lib/utils";
import { reactiveOmit } from "@vueuse/core";
import type { SliderRootEmits, SliderRootProps } from "reka-ui";
import { SliderRange, SliderRoot, SliderThumb, SliderTrack, useForwardPropsEmits } from "reka-ui";
import { type HTMLAttributes } from "vue";

const props = defineProps<SliderRootProps & { class?: HTMLAttributes["class"] }>();
const emits = defineEmits<SliderRootEmits>();

const delegatedProps = reactiveOmit(props, "class");

const forwarded = useForwardPropsEmits(delegatedProps, emits);

const positions = (modelValue: number[] | null = []) => {
  console.log("positions", modelValue, delegatedProps.min, delegatedProps.max);
  const mappedValues = (modelValue ?? []).map((val) =>
    val < delegatedProps!.min! ? delegatedProps.min! : val,
  );

  return mappedValues.map(
    (val) =>
      ((val - (delegatedProps.min ?? 0)) /
        ((delegatedProps.max ?? 1) - (delegatedProps.min ?? 0))) *
      100,
  );
};
</script>

<template>
  <SliderRoot
    v-slot="{ modelValue }"
    data-slot="slider"
    :class="
      cn(
        'relative flex w-full touch-none items-center select-none data-[orientation=vertical]:h-full data-[orientation=vertical]:w-full data-[orientation=vertical]:flex-col',
        props.class,
      )
    "
    v-bind="forwarded"
    orientation="vertical"
  >
    <SliderTrack
      data-slot="slider-track"
      class="bg-primary/10 relative h-1.5 w-full grow overflow-hidden rounded-2xl data-[orientation=vertical]:w-full"
    >
      <SliderRange
        data-slot="slider-range"
        class="bg-primary/90 absolute h-full data-[orientation=vertical]:w-full"
      />
    </SliderTrack>
    <SliderThumb
      v-for="pos in positions(modelValue)"
      :key="pos"
      :style="{ bottom: pos + '%' }"
      data-slot="slider-thumb"
      class="transition-color border-primary/90 bg-background ring-offset-background focus-visible:ring-ring absolute block h-3 w-10 translate-y-[65%] cursor-pointer rounded-full border-2 focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-none disabled:pointer-events-none disabled:cursor-default disabled:opacity-50"
    />
  </SliderRoot>
</template>
