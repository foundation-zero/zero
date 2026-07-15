<script setup lang="ts">
import {
  TooltipListItem,
  TooltipListItemTitle,
  TooltipListItemValue,
} from "@/modules/thrapp/components/tooltip-list";
import { FieldRenderer } from "../../renderers";

defineProps<{
  size?: "sm" | "default";
  noSource?: boolean;
}>();
</script>

<template>
  <TooltipListItem :size="size">
    <TooltipListItemTitle>
      <slot />
      <slot
        v-if="!noSource"
        name="source"
      >
        <FieldRenderer.Source>
          <slot name="sourceName" />
        </FieldRenderer.Source>
      </slot>
    </TooltipListItemTitle>
    <TooltipListItemValue>
      <slot name="value">
        <FieldRenderer.Auto />
      </slot>
    </TooltipListItemValue>
  </TooltipListItem>
</template>
