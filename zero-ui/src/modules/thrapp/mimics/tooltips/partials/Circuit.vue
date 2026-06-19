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

const { items, sources } = useTranslations();

defineProps<ExtractSensorFields<MimicComponentType.ExchangeCircuit>>();
</script>

<template>
  <SensorValue
    :source="sensors.deltaT"
    field="deltaT"
  >
    <TooltipListItem>
      <TooltipListItemTitle>
        {{ items("deltaTemperature") }}
        <FieldRenderer.Source>{{ sources("calculated") }}</FieldRenderer.Source>
      </TooltipListItemTitle>
      <TooltipListItemValue>
        <FieldRenderer.DeltaT />
      </TooltipListItemValue>
    </TooltipListItem>
  </SensorValue>
  <SensorValue
    :source="sensors.incoming"
    field="temperature"
  >
    <TooltipListItem size="sm">
      <TooltipListItemTitle>
        {{ items("incomingTemperature") }}
        <FieldRenderer.Source />
      </TooltipListItemTitle>
      <TooltipListItemValue>
        <FieldRenderer.Temperature />
      </TooltipListItemValue>
    </TooltipListItem>
  </SensorValue>
  <SensorValue
    :source="sensors.outgoing"
    field="temperature"
  >
    <TooltipListItem size="sm">
      <TooltipListItemTitle>
        {{ items("outgoingTemperature") }}
        <FieldRenderer.Source />
      </TooltipListItemTitle>
      <TooltipListItemValue>
        <FieldRenderer.Temperature />
      </TooltipListItemValue>
    </TooltipListItem>
  </SensorValue>
  <SensorValue
    :source="sensors.flow"
    field="flow"
  >
    <TooltipListItem size="sm">
      <TooltipListItemTitle>
        {{ items("flow") }}
        <FieldRenderer.Source />
      </TooltipListItemTitle>
      <TooltipListItemValue>
        <FieldRenderer.FlowRate />
      </TooltipListItemValue>
    </TooltipListItem>
  </SensorValue>
</template>
