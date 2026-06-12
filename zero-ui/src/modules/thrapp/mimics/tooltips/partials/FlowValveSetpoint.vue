<script setup lang="ts">
import {
  TooltipListItem,
  TooltipListItemTitle,
  TooltipListItemValue,
} from "@/modules/thrapp/components/tooltip-list";
import { ControlComponentType } from "@/modules/thrs/types";
import { useTranslations } from "..";
import { ControlValue, ModuleField } from "../../providers";
import { FieldRenderer } from "../../renderers";

const { items } = useTranslations();

defineProps<{ valve: ModuleField<ControlComponentType.Valve> }>();
</script>

<template>
  <ControlValue
    :source="valve"
    field="setpoint"
  >
    <TooltipListItem>
      <TooltipListItemTitle>
        {{ items("setpoint") }}
        <slot />
      </TooltipListItemTitle>
      <TooltipListItemValue>
        <FieldRenderer.Percentage />
      </TooltipListItemValue>
    </TooltipListItem>
  </ControlValue>
</template>
