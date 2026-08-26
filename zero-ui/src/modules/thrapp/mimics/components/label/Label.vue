<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";
import { LabelProps } from ".";

const props = withDefaults(
  defineProps<
    {
      class?: HTMLAttributes["class"];
    } & LabelProps
  >(),
  {
    offsetY: -7.5,
    x: 0,
    width: 140,
    height: 60,
    targetX: 0,
    targetWidth: 0,
  },
);
</script>

<template>
  <svg
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
          :class="cn('bg-background inline-flex flex-col rounded-[0.125rem] px-1', props.class)"
        >
          <header class="text-muted-foreground text-3xs">
            <slot />
          </header>
          <p
            v-if="$slots['value']"
            class="text-foreground text-sm font-medium"
          >
            <slot name="value" />
          </p>
        </hgroup>
      </div>
    </foreignObject>
  </svg>
</template>
