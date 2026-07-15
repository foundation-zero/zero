<script setup lang="ts">
import { TooltipListItem, TooltipListItemTitle } from "@/modules/thrapp/components/tooltip-list";
import { ControllerStateComponentType } from "@/modules/thrs/types";
import _1053 from "../../modules/dhw/data/boiler-tanks/_1053";
import _1054 from "../../modules/dhw/data/boiler-tanks/_1054";
import _1055 from "../../modules/dhw/data/boiler-tanks/_1055";
import { ControllerStateValue, ModuleField } from "../../providers";
import { FieldRenderer } from "../../renderers/index.ts";
import { useTranslations } from "../index.ts";

const { items, sources } = useTranslations();

defineProps<{
  controller: ModuleField<ControllerStateComponentType.DhwTanksController>;
}>();
</script>

<template>
  <ControllerStateValue
    :source="controller"
    field="tank1State"
  >
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
        <FieldRenderer.Source :source="_1053.source" />
        <FieldRenderer.Source :source="_1053.parameters.disabled" />
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
        <FieldRenderer.Source :source="_1054.source" />
        <FieldRenderer.Source :source="_1054.parameters.disabled" />
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
        <FieldRenderer.Source :source="_1055.source" />
        <FieldRenderer.Source :source="_1055.parameters.disabled" />
      </TooltipListItemTitle>
      <FieldRenderer.BoilerTankMode />
    </TooltipListItem>
  </ControllerStateValue>
</template>
