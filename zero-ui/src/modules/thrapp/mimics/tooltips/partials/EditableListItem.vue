<script setup lang="ts">
import {
  TooltipListItem,
  TooltipListItemTitle,
  TooltipListItemValue,
} from "@/modules/thrapp/components/tooltip-list";
import { type Component } from "vue";
import { FieldEditor } from "../../editors";
import { ModuleField } from "../../providers";
import { FieldRenderer } from "../../renderers";

withDefaults(
  defineProps<{
    size?: "sm" | "default";
    renderer?: Component;
    editor?: Component;
    source?: ModuleField;
    noSource?: boolean;
  }>(),
  { size: "default", renderer: FieldRenderer.Auto, editor: FieldEditor.Auto },
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

    <slot name="editor">
      <TooltipListItemValue>
        <component :is="editor">
          <slot name="renderer">
            <component :is="renderer" />
          </slot>
        </component>
      </TooltipListItemValue>
    </slot>
  </TooltipListItem>
</template>
