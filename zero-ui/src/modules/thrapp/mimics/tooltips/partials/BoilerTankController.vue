<script setup lang="ts">
import { TooltipListItem, TooltipListItemTitle } from "@/modules/thrapp/components/tooltip-list";
import { ControllerStateComponentType } from "@/modules/thrs/types";
import { ControllerStateValue, ModuleField } from "../../providers";
import { FieldRenderer } from "../../renderers/index.ts";
import { useTranslations } from "../index.ts";

const { items, sources } = useTranslations();

defineProps<{
  controller: ModuleField<ControllerStateComponentType.DhwTanksController>;
}>();
</script>

<template>
  <ControllerStateValue :source="controller">
    <TooltipListItem>
      <TooltipListItemTitle>
        <slot>{{ items("tankController") }}</slot>
      </TooltipListItemTitle>
      <FieldRenderer.HeatPumpMode />
    </TooltipListItem>
  </ControllerStateValue>

  <ControllerStateValue
    :source="controller"
    field="tank1State"
  >
    <TooltipListItem size="sm">
      <TooltipListItemTitle>
        {{ items("tank1") }}
        <FieldRenderer.Source external>1053</FieldRenderer.Source>
        <FieldRenderer.Source url>{{ sources("tank1") }}</FieldRenderer.Source>
      </TooltipListItemTitle>
      <FieldRenderer.BoilerTankMode />
    </TooltipListItem>
  </ControllerStateValue>

  <ControllerStateValue
    :source="controller"
    field="tank2State"
  >
    <TooltipListItem size="sm">
      <TooltipListItemTitle>
        {{ items("tank2") }}
        <FieldRenderer.Source external>1054</FieldRenderer.Source>
        <FieldRenderer.Source url>{{ sources("tank2") }}</FieldRenderer.Source>
      </TooltipListItemTitle>
      <FieldRenderer.BoilerTankMode />
    </TooltipListItem>
  </ControllerStateValue>

  <ControllerStateValue
    :source="controller"
    field="tank3State"
  >
    <TooltipListItem size="sm">
      <TooltipListItemTitle>
        {{ items("tank3") }}
        <FieldRenderer.Source external>1055</FieldRenderer.Source>
        <FieldRenderer.Source url>{{ sources("tank3") }}</FieldRenderer.Source>
      </TooltipListItemTitle>
      <FieldRenderer.BoilerTankMode />
    </TooltipListItem>
  </ControllerStateValue>
</template>
