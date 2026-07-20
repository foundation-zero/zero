<script setup lang="ts">
import { TooltipListItem, TooltipListItemTitle } from "@/modules/thrapp/components/tooltip-list";
import { type Component } from "vue";
import { FieldEditor } from "../../editors";
import { FieldRenderer } from "../../renderers";

withDefaults(
  defineProps<{
    size?: "sm" | "default";
    renderer?: Component;
    editor?: Component;
  }>(),
  { size: "default", renderer: FieldRenderer.Auto, editor: FieldEditor.Auto },
);
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
      <component :is="editor">
        <slot name="renderer">
          <component :is="renderer" />
        </slot>
      </component>
    </slot>
  </TooltipListItem>
</template>
