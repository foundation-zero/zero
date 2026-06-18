<script setup lang="ts">
import { useTranslations } from ".";
import { MimicTooltip, TooltipComponentContext } from "../../components/tooltip";
import {
  TooltipList,
  TooltipListHeader,
  TooltipListItem,
  TooltipListItemAction,
  TooltipListItemTitle,
  TooltipListItemValue,
} from "../../components/tooltip-list";
import { MimicComponentType } from "../../types";
import { YardTag } from "../components/yard-tag/index.ts";
import SwitchValveInstance from "../instances/SwitchValveInstance.vue";
import { ControlValue } from "../providers/index.ts";
import { FieldRenderer } from "../renderers/index.ts";
import BoilerTankController from "./partials/BoilerTankController.vue";
import BoilerTankOperator from "./partials/BoilerTankOperator.vue";
import ComponentInfo from "./partials/ComponentInfo.vue";
import ManualControl from "./partials/ManualControl.vue";
import ValvePosition from "./partials/ValvePosition.vue";

const props = defineProps<TooltipComponentContext<MimicComponentType.SwitchValve>>();

const { labels, items } = useTranslations();
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <SwitchValveInstance v-bind="props" />
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <TooltipList class="border-b-0">
      <ComponentInfo :tooltip="tooltip" />
      <ManualControl />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("input") }}</TooltipListHeader>
      <ControlValue
        :source="controls.valve"
        field="setpoint"
      >
        <TooltipListItem>
          <TooltipListItemTitle>
            {{ items("setpoint") }}
            <FieldRenderer.Source :source="custom.tank?.controller" />
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.ValveState />
          </TooltipListItemValue>
        </TooltipListItem>
      </ControlValue>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("output") }}</TooltipListHeader>
      <ValvePosition :valve="sensors.valve" />
    </TooltipList>

    <TooltipList v-if="custom.tank">
      <TooltipListHeader>
        {{ labels("controls") }}
        <TooltipListItemAction>{{ labels("viewControls") }}</TooltipListItemAction>
      </TooltipListHeader>
      <BoilerTankController
        v-if="custom.tank?.controller"
        :controller="custom.tank.controller"
      >
        {{ items("tankSelector") }}
      </BoilerTankController>
      <template v-if="custom.tank?.operator">
        <TooltipListItem>
          <TooltipListItemTitle>
            {{ custom.tank.operatorName }}
          </TooltipListItemTitle>
        </TooltipListItem>
        <BoilerTankOperator :sensors="custom.tank.operator" />
      </template>
    </TooltipList>
  </MimicTooltip>
</template>
