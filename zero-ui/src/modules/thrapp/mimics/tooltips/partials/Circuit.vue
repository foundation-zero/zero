<script setup lang="ts">
import {
  TooltipListItem,
  TooltipListItemTitle,
  TooltipListItemValue,
} from "@/modules/thrapp/components/tooltip-list";
import { MimicComponentType } from "@/modules/thrapp/types";
import { ExtractSensorFields } from "@/modules/thrapp/types/fields";
import { useTranslations } from "..";
import { SensorValue } from "../../providers";
import { FieldRenderer } from "../../renderers";

const { items } = useTranslations();

defineProps<ExtractSensorFields<MimicComponentType.HeatExchanger>>();
</script>

<template>
  <SensorValue :source="sensors.incoming">
    <TooltipListItem size="sm">
      <TooltipListItemTitle>
        {{ items("incomingTemperature") }}
        <FieldRenderer.Source />
      </TooltipListItemTitle>
      <TooltipListItemValue>
        <FieldRenderer.Auto />
      </TooltipListItemValue>
    </TooltipListItem>
  </SensorValue>
  <SensorValue :source="sensors.outgoing">
    <TooltipListItem size="sm">
      <TooltipListItemTitle>
        {{ items("outgoingTemperature") }}
        <FieldRenderer.Source />
      </TooltipListItemTitle>
      <TooltipListItemValue>
        <FieldRenderer.Auto />
      </TooltipListItemValue>
    </TooltipListItem>
  </SensorValue>
  <SensorValue :source="sensors.flow">
    <TooltipListItem size="sm">
      <TooltipListItemTitle>
        {{ items("flow") }}
        <FieldRenderer.Source />
      </TooltipListItemTitle>
      <TooltipListItemValue>
        <FieldRenderer.Auto />
      </TooltipListItemValue>
    </TooltipListItem>
  </SensorValue>
</template>
