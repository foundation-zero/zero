<script setup lang="ts">
import {
  TooltipListItem,
  TooltipListItemTitle,
} from "@/modules/heat-system/components/tooltip-list";
import { BoilerTankStateField } from "@/modules/heat-system/types";
import {
  ControllerStateComponentType,
  ParametersType,
} from "@/modules/heat-system-simulation/types/index.ts";
import * as Partials from ".";
import { ControllerStateValue, ModuleField } from "../../providers";
import { FieldRenderer } from "../../renderers/index.ts";
import { useTranslations } from "../index.ts";
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
