<script setup lang="ts">
import {
  TooltipListItem,
  TooltipListItemTitle,
  TooltipListItemValue,
} from "@/modules/thrapp/components/tooltip-list";
import { SensorComponentType } from "@/modules/thrs/types";
import { useTranslations } from "..";
import { ModuleField, SensorValue } from "../../providers";
import { FieldRenderer } from "../../renderers";

const { items } = useTranslations();

defineProps<{ valve: ModuleField<SensorComponentType.Valve> }>();
</script>

<template>
  <SensorValue
    :source="valve"
    field="positionRel"
  >
    <TooltipListItem>
      <TooltipListItemTitle>{{ items("relativePosition") }}</TooltipListItemTitle>
      <TooltipListItemValue>
        <FieldRenderer.Percentage />
      </TooltipListItemValue>
    </TooltipListItem>
    <TooltipListItem>
      <TooltipListItemTitle>{{ items("absolutePosition") }}</TooltipListItemTitle>
      <TooltipListItemValue>
        <FieldRenderer.PositionAbsolute />
      </TooltipListItemValue>
    </TooltipListItem>
  </SensorValue>
</template>
