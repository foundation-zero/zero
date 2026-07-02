<script setup lang="ts">
import { BoilerTankState } from "@/modules/thrs/types";
import { computed } from "vue";
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
import { DHW_TANK_CAPACITY } from "../../utils/consts.ts";
import { YardTag } from "../components/yard-tag";
import BoilerTankInstance from "../instances/BoilerTankInstance.vue";
import { ControllerStateValue, getMimicDataProvider, ParameterValue } from "../providers";
import SensorValue from "../providers/SensorValue.vue";
import { FieldRenderer } from "../renderers/index.ts";
import BoilerTankController from "./partials/BoilerTankController.vue";
import BoilerTankOperator from "./partials/BoilerTankOperator.vue";
import ComponentInfo from "./partials/ComponentInfo.vue";
import ManualControl from "./partials/ManualControl.vue";

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
      <BoilerTankInstance v-bind="props" />
      <YardTag class="text-sm">{{ tooltip?.yardTag }}</YardTag>
    </div>

    <TooltipList class="border-b-0">
      <ComponentInfo :tooltip="tooltip" />
      <ManualControl />
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("input") }}</TooltipListHeader>
      <ControllerStateValue
        :source="controllerState.controller"
        :field="custom.tankStateField"
      >
        <TooltipListItem>
          <TooltipListItemTitle>
            {{ items("state") }}
            <FieldRenderer.Source external>{{ sources("tankState") }}</FieldRenderer.Source>
          </TooltipListItemTitle>
          <FieldRenderer.BoilerTankMode />
        </TooltipListItem>
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
        <TooltipListItem size="sm">
          <TooltipListItemTitle>
            {{ items("currentTemperature") }}
            <FieldRenderer.Source />
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.Temperature />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>

      <SensorValue
        :source="sensors.boostingSupply"
        field="temperature"
      >
        <TooltipListItem size="sm">
          <TooltipListItemTitle>
            {{ items("incomingTemperature") }}
            <FieldRenderer.Source />
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.Temperature />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>

      <ParameterValue :source="parameters.minimumTemperature">
        <TooltipListItem size="sm">
          <TooltipListItemTitle>
            {{ items("minTemperature") }}
            <FieldRenderer.Source url>{{ sources("minTemperature") }}</FieldRenderer.Source>
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.Temperature />
          </TooltipListItemValue>
        </TooltipListItem>
      </ParameterValue>

      <ParameterValue :source="parameters.maximumTemperature">
        <TooltipListItem size="sm">
          <TooltipListItemTitle>
            {{ items("maxTemperature") }}
            <FieldRenderer.Source url>{{ sources("maxTemperature") }}</FieldRenderer.Source>
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.Temperature />
          </TooltipListItemValue>
        </TooltipListItem>
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

        <TooltipListItem size="sm">
          <TooltipListItemTitle>
            {{ items("fill") }}
            <FieldRenderer.Source />
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.Level />
          </TooltipListItemValue>
        </TooltipListItem>
      </SensorValue>

      <TooltipListItem size="sm">
        <TooltipListItemTitle>
          {{ items("capacity") }}
          <FieldRenderer.Source>{{ sources("capacity") }}</FieldRenderer.Source>
        </TooltipListItemTitle>
        <TooltipListItemValue>
          <FieldRenderer.Level :value="DHW_TANK_CAPACITY" />
        </TooltipListItemValue>
      </TooltipListItem>

      <ParameterValue :source="parameters.minimumLevel">
        <TooltipListItem size="sm">
          <TooltipListItemTitle>
            {{ items("minLevel") }}
            <FieldRenderer.Source url>{{ sources("minLevel") }}</FieldRenderer.Source>
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.Level />
          </TooltipListItemValue>
        </TooltipListItem>
      </ParameterValue>

      <ParameterValue :source="parameters.maximumLevel">
        <TooltipListItem size="sm">
          <TooltipListItemTitle>
            {{ items("maxLevel") }}
            <FieldRenderer.Source url>{{ sources("maxLevel") }}</FieldRenderer.Source>
          </TooltipListItemTitle>
          <TooltipListItemValue>
            <FieldRenderer.Level />
          </TooltipListItemValue>
        </TooltipListItem>
      </ParameterValue>

      <ControllerStateValue
        :source="controllerState.controller"
        :field="custom.tankStateField"
      >
        <template #default="{ value }">
          <ControllerStateValue
            :source="controllerState.controller"
            field="timeToFill"
          >
            <TooltipListItem v-if="value === BoilerTankState.Filling">
              <TooltipListItemTitle>{{ items("estimatedFillingTime") }}</TooltipListItemTitle>
              <TooltipListItemValue>
                <FieldRenderer.TimeRemaining />
              </TooltipListItemValue>
            </TooltipListItem>
          </ControllerStateValue>
        </template>
        <!-- <TooltipListItem>
        <TooltipListItemTitle>{{ items("estimatedTimeToHeat") }}</TooltipListItemTitle>
        <TooltipListItemTimeRemaining :value="0" />
      </TooltipListItem> -->
      </ControllerStateValue>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>
        {{ labels("controls") }}
        <TooltipListItemAction>{{ labels("viewControls") }}</TooltipListItemAction>
      </TooltipListHeader>
      <BoilerTankController :controller="controllerState.controller" />
      <BoilerTankOperator :sensors="sensors" />
    </TooltipList>
  </MimicTooltip>
</template>
