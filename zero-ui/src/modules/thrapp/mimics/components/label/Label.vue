<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes, useSlots } from "vue";
import { LabelProps } from ".";
import { useLabelVisibility } from "./label.utils";

const props = withDefaults(
  defineProps<
    {
      class?: HTMLAttributes["class"];
    } & LabelProps
  >(),
  {
    x: 0,
    width: 80,
    height: 40,
    targetX: 0,
    targetWidth: 0,
    minWidth: 35,
  },
);

const slots = useSlots();
const { showTag, showValue, isVisible } = useLabelVisibility({
  hasValue: () => !!slots.value,
  unfiltered: () => props.unfiltered,
});
</script>

<template>
  <svg
    v-show="isVisible"
    :width="width"
    :height="height"
    :x="Number(x) > 0 ? x : Number(targetX) + Number(targetWidth) / 2 - Number(width) / 2"
    :y="y"
  >
    <!-- Offset on y needed because of hgroup positioning within the foreignObject -->
    <foreignObject
      :width="width"
      :height="height"
    >
      <div
        class="h-full w-full"
        :class="{ 'flex flex-col items-center': targetWidth != 0 && targetX != 0 }"
      >
        <hgroup
          xmlns="http://www.w3.org/1999/xhtml"
          :class="
            cn('bg-background inline-flex min-w-8 flex-col rounded-[0.125rem] px-1', props.class)
          "
          :style="{ minWidth: showValue ? minWidth + 'px' : undefined }"
        >
          <header
            v-show="showTag"
            class="text-muted-foreground text-3xs"
          >
            <slot />
          </header>
          <p
            v-if="$slots['value']"
            v-show="showValue"
            class="text-foreground text-xs font-medium"
          >
            <slot name="value" />
          </p>
        </hgroup>
      </div>
    </foreignObject>
  </svg>
</template>
