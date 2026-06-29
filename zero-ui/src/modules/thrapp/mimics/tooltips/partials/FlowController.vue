<script setup lang="ts">
import { formatNumber } from "@/modules/common/lib/utils.ts";
import {
  TooltipListItem,
  TooltipListItemTitle,
  TooltipListItemValue,
} from "@/modules/thrapp/components/tooltip-list";
import { ControlComponentType, ParametersType, SensorComponentType } from "@/modules/thrs/types";
import { snakeCase } from "lodash";
import { ControlValue, ModuleField } from "../../providers";
import { FieldRenderer } from "../../renderers/index.ts";
import { useTranslations } from "../index.ts";

const { items, sources } = useTranslations();

defineProps<{
  controller: ModuleField<ControlComponentType.PIDController>;
  setpoint: ModuleField<ParametersType.Flow>;
  measurement: ModuleField<SensorComponentType.Flow>;
}>();
</script>

<template>
  <ControlValue
    :source="controller"
    field="enabled"
  >
    <TooltipListItem>
      <TooltipListItemTitle>
        <slot>
          <FieldRenderer.Source external>{{ snakeCase(controller[2]) }}</FieldRenderer.Source>
        </slot>
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
        <slot name="actuator">
          <FieldRenderer.Source>{{ sources("this") }}</FieldRenderer.Source>
        </slot>
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
        <slot name="setpoint">
          <FieldRenderer.Source
            url
            :source="setpoint"
          />
        </slot>
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
      <!-- TODO: "This component" means that measurement sensor is currently selected sensor? -->
      <TooltipListItemTitle>
        {{ items("measurement") }}
        <slot name="measurement">
          <FieldRenderer.Source :source="measurement" />
        </slot>
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
