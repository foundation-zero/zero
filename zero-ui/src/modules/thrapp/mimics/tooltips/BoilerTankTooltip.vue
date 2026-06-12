<script setup lang="ts">
import { formatInt, ratioAsPercentage } from "@/modules/common/lib/utils.ts";
import { BoilerTankState } from "@/modules/thrs/types";
import { computed } from "vue";
import { useTranslations } from ".";
import { MimicTooltip, TooltipComponentContext } from "../../components/tooltip";
import {
  TooltipList,
  TooltipListHeader,
  TooltipListItem,
  TooltipListItemAction,
  TooltipListItemNumber,
  TooltipListItemSource,
  TooltipListItemTimeRemaining,
  TooltipListItemTitle,
  TooltipListItemValue,
} from "../../components/tooltip-list";
import { MimicComponentType } from "../../types";
import { BOILER_TANK_CAPACITY } from "../../utils/consts.ts";
import { BoilerTankMode } from "../components/boiler-tank/index.ts";
import { YardTag } from "../components/yard-tag";
import BoilerTankInstance from "../instances/BoilerTankInstance.vue";
import { getMimicDataProvider } from "../providers";
import BoilerTankController from "./partials/BoilerTankController.vue";
import BoilerTankOperator from "./partials/BoilerTankOperator.vue";
import ComponentInfo from "./partials/ComponentInfo.vue";
import ManualControl from "./partials/ManualControl.vue";

const props = defineProps<TooltipComponentContext<MimicComponentType.BoilerTank>>();
const { sensors, parameters, controls, custom, tooltip } = props;

const { sources, labels, items, units } = useTranslations();
const { getSensorValue, getParameterValue, getControlValue } = getMimicDataProvider();

const currentTemperature = getSensorValue(sensors.temperature);
const boostingSupplyValue = getSensorValue(sensors.boostingSupply);
const minimumTemperature = getParameterValue(parameters.minimumTemperature);
const maximumTemperature = getParameterValue(parameters.maximumTemperature);
const minimumLevel = getParameterValue(parameters.minimumLevel);
const maximumLevel = getParameterValue(parameters.maximumLevel);
const controller = getControlValue(controls.controller);
const currentLevel = getSensorValue(sensors.level);

const currentLevelPercentage = ratioAsPercentage(
  computed(() => (currentLevel.value?.level.value ?? 0) / BOILER_TANK_CAPACITY),
);

const boilerState = computed(() => controller.value?.[custom.tankStateField].value);
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
      <TooltipListItem>
        <TooltipListItemTitle>
          {{ items("state") }}
          <TooltipListItemSource external>{{ sources("tankState") }}</TooltipListItemSource>
        </TooltipListItemTitle>
        <BoilerTankMode :mode="boilerState" />
      </TooltipListItem>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ labels("output") }}</TooltipListHeader>
      <TooltipListItem>
        <TooltipListItemTitle>{{ items("temperature") }}</TooltipListItemTitle>
        <TooltipListItemValue>On temperature</TooltipListItemValue>
      </TooltipListItem>
      <TooltipListItem size="sm">
        <TooltipListItemTitle>
          {{ items("currentTemperature") }}
          <TooltipListItemSource :source="sensors.temperature" />
        </TooltipListItemTitle>
        <TooltipListItemNumber
          :value="currentTemperature?.temperature.value"
          :unit="units('celsius')"
          :format="formatInt"
        />
      </TooltipListItem>
      <TooltipListItem size="sm">
        <TooltipListItemTitle>
          {{ items("incomingTemperature") }}
          <TooltipListItemSource :source="sensors.boostingSupply" />
        </TooltipListItemTitle>
        <TooltipListItemNumber
          :value="boostingSupplyValue?.temperature.value"
          :unit="units('celsius')"
          :format="formatInt"
        />
      </TooltipListItem>
      <TooltipListItem size="sm">
        <TooltipListItemTitle>
          {{ items("minTemperature") }}
          <TooltipListItemSource url>{{ sources("minTemperature") }}</TooltipListItemSource>
        </TooltipListItemTitle>
        <TooltipListItemNumber
          :value="minimumTemperature"
          :unit="units('celsius')"
          :format="formatInt"
        />
      </TooltipListItem>
      <TooltipListItem size="sm">
        <TooltipListItemTitle>
          {{ items("maxTemperature") }}
          <TooltipListItemSource url>{{ sources("maxTemperature") }}</TooltipListItemSource>
        </TooltipListItemTitle>
        <TooltipListItemNumber
          :value="maximumTemperature"
          :unit="units('celsius')"
          :format="formatInt"
        />
      </TooltipListItem>
      <TooltipListItem>
        <TooltipListItemTitle>{{ items("filling") }}</TooltipListItemTitle>
        <TooltipListItemNumber
          :value="currentLevelPercentage"
          :unit="units('percent')"
          :format="formatInt"
          dense
        />
      </TooltipListItem>
      <TooltipListItem size="sm">
        <TooltipListItemTitle>
          {{ items("levelSensor") }}
          <TooltipListItemSource :source="sensors.level" />
        </TooltipListItemTitle>
        <TooltipListItemValue>Not empty</TooltipListItemValue>
      </TooltipListItem>
      <TooltipListItem size="sm">
        <TooltipListItemTitle>
          {{ items("fill") }}
          <TooltipListItemSource :source="sensors.level" />
        </TooltipListItemTitle>
        <TooltipListItemNumber
          :value="currentLevel?.level.value"
          :format="formatInt"
          :unit="units('liters')"
        />
      </TooltipListItem>
      <TooltipListItem size="sm">
        <TooltipListItemTitle>
          {{ items("capacity") }}
          <TooltipListItemSource>{{ sources("capacity") }}</TooltipListItemSource>
        </TooltipListItemTitle>
        <TooltipListItemNumber
          :value="BOILER_TANK_CAPACITY"
          :format="formatInt"
          :unit="units('liters')"
        />
      </TooltipListItem>
      <TooltipListItem size="sm">
        <TooltipListItemTitle>
          {{ items("minLevel") }}
          <TooltipListItemSource url>{{ sources("minLevel") }}</TooltipListItemSource>
        </TooltipListItemTitle>
        <TooltipListItemNumber
          :value="minimumLevel"
          :format="formatInt"
          :unit="units('liters')"
        />
      </TooltipListItem>
      <TooltipListItem size="sm">
        <TooltipListItemTitle>
          {{ items("maxLevel") }}
          <TooltipListItemSource url>{{ sources("maxLevel") }}</TooltipListItemSource>
        </TooltipListItemTitle>
        <TooltipListItemNumber
          :value="maximumLevel"
          :format="formatInt"
          :unit="units('liters')"
        />
      </TooltipListItem>
      <TooltipListItem v-if="boilerState === BoilerTankState.Filling">
        <TooltipListItemTitle>{{ items("estimatedFillingTime") }}</TooltipListItemTitle>
        <TooltipListItemTimeRemaining :value="controller?.timeToFill.value" />
      </TooltipListItem>
      <!-- <TooltipListItem>
        <TooltipListItemTitle>{{ items("estimatedTimeToHeat") }}</TooltipListItemTitle>
        <TooltipListItemTimeRemaining :value="0" />
      </TooltipListItem> -->
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>
        {{ labels("controls") }}
        <TooltipListItemAction>{{ labels("viewControls") }}</TooltipListItemAction>
      </TooltipListHeader>
      <BoilerTankController :controller="controls.controller" />
      <BoilerTankOperator :sensors="sensors" />
    </TooltipList>
  </MimicTooltip>
</template>
