<script setup lang="ts">
import { BoilerTankState } from "@/modules/thrsim/types/index.ts";
import { computed } from "vue";
import { useTranslations } from ".";
import {
  MimicTooltip,
  NoopTooltipProvider,
  TooltipComponentContext,
} from "../../components/tooltip";
import {
  TooltipList,
  TooltipListHeader,
  TooltipListItem,
  TooltipListItemAction,
  TooltipListItemTitle,
  TooltipListItemValue,
} from "../../components/tooltip-list";

import { MimicComponentType } from "../../types";
import { DHW_TANK_CAPACITY } from "../../utils/consts.ts";
import { YardTag } from "../components/yard-tag";
import BoilerTankInstance from "../instances/BoilerTankInstance.vue";
import { ControllerStateValue, getMimicDataProvider, ParameterValue } from "../providers";
import SensorValue from "../providers/SensorValue.vue";
import { FieldRenderer } from "../renderers/index.ts";
import * as Partials from "./partials";
import BoilerTankController from "./partials/BoilerTankController.vue";
import BoilerTankOperator from "./partials/BoilerTankOperator.vue";
const props = defineProps<TooltipComponentContext<MimicComponentType.BoilerTank>>();
const { sensors, parameters, custom, tooltip } = props;

const { sources, labels, items } = useTranslations();
const { getSensorValue } = getMimicDataProvider();

const currentLevel = getSensorValue(sensors.level);
const currentLevelPercentage = computed(
  () => (currentLevel.value?.level.value ?? 0) / DHW_TANK_CAPACITY,
);
</script>

<template>
  <MimicTooltip>
    <div class="flex items-center gap-2">
      <NoopTooltipProvider>
        <BoilerTankInstance v-bind="props" />
      </NoopTooltipProvider>
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <TooltipList class="border-b-0">
      <Partials.ComponentInfo :tooltip="tooltip" />
      <Partials.ManualControl />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("input") }}</TooltipListHeader>
      <ControllerStateValue
        :source="controllerState.controller"
        :field="custom.tankStateField"
      >
        <Partials.ListItem>
          {{ items("state") }}
          <template #sourceName>
            {{ sources("tankState") }}
          </template>
          <template #value>
            <FieldRenderer.BoilerTankMode />
          </template>
        </Partials.ListItem>
      </ControllerStateValue>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("output") }}</TooltipListHeader>
      <TooltipListItem>
        <TooltipListItemTitle>{{ items("temperature") }}</TooltipListItemTitle>
        <TooltipListItemValue>On temperature</TooltipListItemValue>
      </TooltipListItem>

      <SensorValue
        :source="sensors.temperature"
        field="temperature"
      >
        <Partials.ListItem size="sm">
          {{ items("currentTemperature") }}
        </Partials.ListItem>
      </SensorValue>

      <SensorValue
        :source="sensors.boostingSupply"
        field="temperature"
      >
        <Partials.ListItem size="sm">
          {{ items("incomingTemperature") }}
        </Partials.ListItem>
      </SensorValue>

      <ParameterValue :source="parameters.minimumTemperature">
        <Partials.ListItem
          size="sm"
          :renderer="FieldRenderer.Temperature"
        >
          {{ items("minTemperature") }}
        </Partials.ListItem>
      </ParameterValue>

      <ParameterValue :source="parameters.maximumTemperature">
        <Partials.ListItem
          size="sm"
          :renderer="FieldRenderer.Temperature"
        >
          {{ items("maxTemperature") }}
        </Partials.ListItem>
      </ParameterValue>

      <TooltipListItem>
        <TooltipListItemTitle>{{ items("filling") }}</TooltipListItemTitle>
        <TooltipListItemValue>
          <FieldRenderer.Percentage :value="currentLevelPercentage" />
        </TooltipListItemValue>
      </TooltipListItem>

      <SensorValue
        :source="sensors.level"
        field="level"
      >
        <TooltipListItem size="sm">
          <TooltipListItemTitle>
            {{ items("levelSensor") }}
            <FieldRenderer.Source />
          </TooltipListItemTitle>
          <TooltipListItemValue>Not empty</TooltipListItemValue>
        </TooltipListItem>

        <Partials.ListItem size="sm">
          {{ items("fill") }}
        </Partials.ListItem>
      </SensorValue>

      <Partials.ListItem size="sm">
        {{ items("capacity") }}
        <template #sourceName>
          {{ sources("capacity") }}
        </template>
        <template #renderer>
          <FieldRenderer.Level :value="DHW_TANK_CAPACITY" />
        </template>
      </Partials.ListItem>

      <ParameterValue :source="parameters.minimumLevel">
        <Partials.ListItem
          size="sm"
          :renderer="FieldRenderer.Level"
        >
          {{ items("minLevel") }}
        </Partials.ListItem>
      </ParameterValue>

      <ParameterValue :source="parameters.maximumLevel">
        <Partials.ListItem
          size="sm"
          :renderer="FieldRenderer.Level"
        >
          {{ items("maxLevel") }}
        </Partials.ListItem>
      </ParameterValue>

      <ControllerStateValue
        :source="controllerState.controller"
        :field="custom.tankStateField"
      >
        <template #default="{ value }">
          <ControllerStateValue
            v-if="value === BoilerTankState.Filling"
            :source="controllerState.controller"
            field="timeToFill"
          >
            <Partials.ListItem size="sm">
              {{ items("estimatedFillingTime") }}
            </Partials.ListItem>
          </ControllerStateValue>
        </template>
      </ControllerStateValue>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>
        {{ labels("controls") }}
        <TooltipListItemAction>{{ labels("viewControls") }}</TooltipListItemAction>
      </TooltipListHeader>
      <BoilerTankController
        :controller="controllerState.controller"
        :enabled-parameter="parameters.enabled"
        :tank-state-field="custom.tankStateField"
      />
      <BoilerTankOperator :sensors="sensors" />
    </TooltipList>
  </MimicTooltip>
</template>
