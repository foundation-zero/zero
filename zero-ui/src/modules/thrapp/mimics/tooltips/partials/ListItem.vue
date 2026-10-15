<script setup lang="ts">
import {
  TooltipListItem,
  TooltipListItemTitle,
  TooltipListItemValue,
} from "@/modules/thrapp/components/tooltip-list";
import { type Component } from "vue";
import { ModuleField } from "../../providers";
import { FieldRenderer } from "../../renderers";

withDefaults(
  defineProps<{
    size?: "sm" | "default";
    source?: ModuleField;
    noSource?: boolean;
    renderer?: Component;
  }>(),
  {
    size: "default",
    noSource: false,
    renderer: FieldRenderer.Auto,
  },
);
</script>

<template>
  <TooltipListItem :size="size">
    <TooltipListItemTitle>
      <slot />
      <slot
        v-if="!noSource"
        name="source"
      >
        <FieldRenderer.Source :source="source">
          <slot name="sourceName" />
        </FieldRenderer.Source>
      </slot>
    </TooltipListItemTitle>
    <slot name="value">
      <TooltipListItemValue>
        <slot name="renderer">
          <component :is="renderer" />
        </slot>
      </TooltipListItemValue>
    </slot>
  </TooltipListItem>
</template>
