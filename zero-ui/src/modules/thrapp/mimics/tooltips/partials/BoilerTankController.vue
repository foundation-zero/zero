<script setup lang="ts">
import { tScoped } from "@/modules/common/lib/utils";
import {
  TooltipListItem,
  TooltipListItemSource,
  TooltipListItemTitle,
} from "@/modules/thrapp/components/tooltip-list";
import { ControlComponentType } from "@/modules/thrs/types";
import { BoilerTankMode } from "../../components/boiler-tank";
import { HeatPumpModes } from "../../components/heat-pump";
import HeatPumpMode from "../../components/heat-pump/HeatPumpMode.vue";
import { getMimicDataProvider, ModuleField } from "../../providers";

const tItems = tScoped("thrapp.tooltips.items");
const tSources = tScoped("thrapp.tooltips.sources");

const { getControlValue } = getMimicDataProvider();

const props = defineProps<{
  controller: ModuleField<ControlComponentType.BoilersTanksController>;
}>();

const controllerValues = getControlValue(props.controller);
</script>

<template>
  <TooltipListItem>
    <TooltipListItemTitle>
      <slot>{{ tItems("tankController") }}</slot>
    </TooltipListItemTitle>
    <HeatPumpMode :mode="HeatPumpModes.Active" />
  </TooltipListItem>
  <TooltipListItem size="sm">
    <TooltipListItemTitle>
      {{ tItems("tank1") }}
      <TooltipListItemSource external>1053</TooltipListItemSource>
      <TooltipListItemSource url>{{ tSources("tank1") }}</TooltipListItemSource>
    </TooltipListItemTitle>
    <BoilerTankMode :mode="controllerValues?.tank1State.value" />
  </TooltipListItem>
  <TooltipListItem size="sm">
    <TooltipListItemTitle>
      {{ tItems("tank2") }}
      <TooltipListItemSource external>1054</TooltipListItemSource>
      <TooltipListItemSource url>{{ tSources("tank2") }}</TooltipListItemSource>
    </TooltipListItemTitle>
    <BoilerTankMode :mode="controllerValues?.tank2State.value" />
  </TooltipListItem>
  <TooltipListItem size="sm">
    <TooltipListItemTitle>
      {{ tItems("tank3") }}
      <TooltipListItemSource external>1055</TooltipListItemSource>
      <TooltipListItemSource url>{{ tSources("tank3") }}</TooltipListItemSource>
    </TooltipListItemTitle>
    <BoilerTankMode :mode="controllerValues?.tank3State.value" />
  </TooltipListItem>
</template>
