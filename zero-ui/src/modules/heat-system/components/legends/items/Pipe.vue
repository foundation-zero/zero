<script setup lang="ts">
import { cn } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";
import { LegendItem, LegendItemInfo, LegendItemPreview, LegendItemTitle } from "../../legend";

const props = defineProps<{
  class?: HTMLAttributes["class"];
}>();
</script>

<template>
  <LegendItem>
    <LegendItemPreview size="sm">
      <slot name="pipe">
        <hr :class="cn('w-9', props.class)" />
      </slot>
    </LegendItemPreview>
    <LegendItemInfo>
      <LegendItemTitle>
        <slot />
      </LegendItemTitle>
    </LegendItemInfo>
  </LegendItem>
</template>
