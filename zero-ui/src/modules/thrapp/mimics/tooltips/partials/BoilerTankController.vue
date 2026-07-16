<script setup lang="ts">
import { TooltipListItem, TooltipListItemTitle } from "@/modules/thrapp/components/tooltip-list";
import { BoilerTankStateField } from "@/modules/thrapp/types";
import { ControllerStateComponentType, ParametersType } from "@/modules/thrs/types";
import * as Partials from ".";
import { ControllerStateValue, ModuleField } from "../../providers";
import { FieldRenderer } from "../../renderers/index.ts";
import { useTranslations } from "../index.ts";
const { items } = useTranslations();

defineProps<{
  controller: ModuleField<ControllerStateComponentType.DhwTanksController>;
  source?: ModuleField;
  tankStateField: BoilerTankStateField;
  disabledParameter: ModuleField<ParametersType.Disabled>;
}>();
</script>

<template>
  <TooltipListItem>
    <TooltipListItemTitle>
      <slot>{{ items("tankController") }}</slot>
    </TooltipListItemTitle>
    <FieldRenderer.BoilerTankControllerMode />
  </TooltipListItem>

  <ControllerStateValue
    :source="controller"
    :field="tankStateField"
  >
    <Partials.ListItem size="sm">
      {{ items("tankState") }}
      <template #source>
        <FieldRenderer.Source
          v-if="source"
          :source="source"
        />
        <FieldRenderer.Source :source="disabledParameter" />
      </template>
      <template #value>
        <FieldRenderer.BoilerTankMode />
      </template>
    </Partials.ListItem>
  </ControllerStateValue>
</template>
