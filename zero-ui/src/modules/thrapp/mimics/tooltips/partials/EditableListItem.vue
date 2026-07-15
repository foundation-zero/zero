<script setup lang="ts">
import { TooltipListItem, TooltipListItemTitle } from "@/modules/thrapp/components/tooltip-list";
import { FieldEditor } from "../../editors";
import { FieldRenderer } from "../../renderers";

defineProps<{
  size?: "sm" | "default";
}>();
</script>

<template>
  <TooltipListItem :size="size">
    <TooltipListItemTitle>
      <slot />
      <slot name="source">
        <FieldRenderer.Source>
          <slot name="sourceName" />
        </FieldRenderer.Source>
      </slot>
    </TooltipListItemTitle>

    <slot name="editor">
      <FieldEditor.Auto>
        <slot name="value">
          <FieldRenderer.Auto />
        </slot>
      </FieldEditor.Auto>
    </slot>
  </TooltipListItem>
</template>
