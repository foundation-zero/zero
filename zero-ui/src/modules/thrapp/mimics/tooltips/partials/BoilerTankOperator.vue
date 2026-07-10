<script setup lang="ts">
import {
  TooltipListItem,
  TooltipListItemTitle,
  TooltipListItemValue,
} from "@/modules/thrapp/components/tooltip-list";
import { ExtractSensorFields } from "@/modules/thrapp/types/fields.ts";
import { MimicComponentType } from "@/modules/thrapp/types/index.ts";
import { useTranslations } from "..";
import { SensorValue } from "../../providers";
import { FieldRenderer } from "../../renderers";

const { items } = useTranslations();

defineProps<ExtractSensorFields<MimicComponentType.BoilerTank>>();
</script>

<template>
  <SensorValue
    :source="sensors.boostReturnValve"
    field="positionRel"
  >
    <TooltipListItem size="sm">
      <TooltipListItemTitle>
        {{ items("boostReturnValve") }}
        <FieldRenderer.Source />
      </TooltipListItemTitle>
      <TooltipListItemValue>
        <FieldRenderer.ValveState />
      </TooltipListItemValue>
    </TooltipListItem>
  </SensorValue>

  <SensorValue
    :source="sensors.boostSupplyValve"
    field="positionRel"
  >
    <TooltipListItem size="sm">
      <TooltipListItemTitle>
        {{ items("boostSupplyValve") }}
        <FieldRenderer.Source />
      </TooltipListItemTitle>
      <TooltipListItemValue>
        <FieldRenderer.ValveState />
      </TooltipListItemValue>
    </TooltipListItem>
  </SensorValue>

  <SensorValue
    :source="sensors.supplyValve"
    field="positionRel"
  >
    <TooltipListItem size="sm">
      <TooltipListItemTitle>
        {{ items("supplyValve") }}
        <FieldRenderer.Source />
      </TooltipListItemTitle>
      <TooltipListItemValue>
        <FieldRenderer.ValveState />
      </TooltipListItemValue>
    </TooltipListItem>
  </SensorValue>

  <SensorValue
    :source="sensors.dischargeValve"
    field="positionRel"
  >
    <TooltipListItem size="sm">
      <TooltipListItemTitle>
        {{ items("dischargeValve") }}
        <FieldRenderer.Source />
      </TooltipListItemTitle>
      <TooltipListItemValue>
        <FieldRenderer.ValveState />
      </TooltipListItemValue>
    </TooltipListItem>
  </SensorValue>
</template>
