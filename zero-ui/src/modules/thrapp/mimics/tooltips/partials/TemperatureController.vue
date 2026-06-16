<script setup lang="ts">
import { formatNumber } from "@/modules/common/lib/utils.ts";
import {
  TooltipListItem,
  TooltipListItemTitle,
  TooltipListItemValue,
} from "@/modules/thrapp/components/tooltip-list";
import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";
import { ControlValue, ModuleField } from "../../providers/index.ts";
import { FieldRenderer } from "../../renderers/index.ts";
import { useTranslations } from "../index.ts";

const { items, sources } = useTranslations();

defineProps<{
  controller: ModuleField<ControlComponentType.PIDController>;
  measurement: ModuleField<SensorComponentType.Temperature>;
  setpointName: string;
}>();
</script>

<template>
  <ControlValue
    :source="controller"
    field="enabled"
  >
    <TooltipListItem>
      <TooltipListItemTitle>
        <slot />
      </TooltipListItemTitle>

      <FieldRenderer.HeatPumpMode />
    </TooltipListItem>
  </ControlValue>

  <ControlValue
    :source="controller"
    field="output"
  >
    <TooltipListItem size="sm">
      <TooltipListItemTitle>
        {{ items("actuator") }}
        <FieldRenderer.Source>{{ sources("this") }}</FieldRenderer.Source>
      </TooltipListItemTitle>
      <TooltipListItemValue>
        <FieldRenderer.Percentage />
      </TooltipListItemValue>
    </TooltipListItem>
  </ControlValue>

  <ControlValue
    :source="controller"
    field="setpoint"
  >
    <TooltipListItem size="sm">
      <TooltipListItemTitle>
        {{ items("setpoint") }}
        <FieldRenderer.Source url>{{ setpointName }}</FieldRenderer.Source>
      </TooltipListItemTitle>
      <TooltipListItemValue>
        <FieldRenderer.Temperature :format="formatNumber(1)" />
      </TooltipListItemValue>
    </TooltipListItem>
  </ControlValue>

  <ControlValue
    :source="controller"
    field="measurement"
  >
    <TooltipListItem size="sm">
      <TooltipListItemTitle>
        {{ items("measurement") }}
        <FieldRenderer.Source />
      </TooltipListItemTitle>
      <TooltipListItemValue>
        <FieldRenderer.Temperature :format="formatNumber(1)" />
      </TooltipListItemValue>
    </TooltipListItem>
  </ControlValue>

  <ControlValue
    :source="controller"
    field="error"
  >
    <TooltipListItem size="sm">
      <TooltipListItemTitle>
        {{ items("error") }}
        <FieldRenderer.Source>{{ sources("calculated") }}</FieldRenderer.Source>
      </TooltipListItemTitle>
      <TooltipListItemValue>
        <FieldRenderer.Temperature :format="formatNumber(1)" />
      </TooltipListItemValue>
    </TooltipListItem>
  </ControlValue>
</template>
