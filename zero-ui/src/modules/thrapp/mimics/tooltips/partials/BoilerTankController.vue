<script setup lang="ts">
import { TooltipListItem, TooltipListItemTitle } from "@/modules/thrapp/components/tooltip-list";
import { BoilerTankStateField } from "@/modules/thrapp/types";
import { ControllerStateComponentType, ParametersType } from "@/modules/thrsim/types";
import * as Partials from ".";
import { useTranslations } from "..";
import { ControllerStateValue, ModuleField } from "../../providers";
import { FieldRenderer } from "../../renderers";
const { items } = useTranslations();

defineProps<{
  controller: ModuleField<ControllerStateComponentType.DhwTanksController>;
  source?: ModuleField;
  tankStateField: BoilerTankStateField;
  enabledParameter: ModuleField<ParametersType.Enabled>;
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
        <FieldRenderer.Source :source="enabledParameter" />
      </template>
      <template #value>
        <FieldRenderer.BoilerTankMode />
      </template>
    </Partials.ListItem>
  </ControllerStateValue>
</template>
