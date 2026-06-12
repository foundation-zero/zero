<script setup lang="ts">
import {
  TooltipListItem,
  TooltipListItemTitle,
  TooltipListItemValue,
} from "@/modules/thrapp/components/tooltip-list";
import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";
import { ControlValue, ModuleField, SensorValue } from "../../providers";
import { FieldRenderer } from "../../renderers/index.ts";
import { useTranslations } from "../index.ts";

const { items, sources } = useTranslations();

defineProps<{
  controller: ModuleField<ControlComponentType.PIDController>;
  measurement: ModuleField<SensorComponentType.Temperature>;
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
      <TooltipListItemValue>
        <FieldRenderer.HeatPumpMode />
      </TooltipListItemValue>
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
        <FieldRenderer.Source url>boilers_filling_temperature</FieldRenderer.Source>
      </TooltipListItemTitle>
      <TooltipListItemValue>
        <FieldRenderer.Temperature />
      </TooltipListItemValue>
    </TooltipListItem>
  </ControlValue>

  <SensorValue
    :source="measurement"
    field="temperature"
  >
    <TooltipListItem size="sm">
      <TooltipListItemTitle>
        {{ items("measurement") }}
        <FieldRenderer.Source :source="measurement" />
      </TooltipListItemTitle>
      <TooltipListItemValue>
        <FieldRenderer.Temperature />
      </TooltipListItemValue>
    </TooltipListItem>
  </SensorValue>

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
        <FieldRenderer.FlowRate />
      </TooltipListItemValue>
    </TooltipListItem>
  </ControlValue>
</template>
