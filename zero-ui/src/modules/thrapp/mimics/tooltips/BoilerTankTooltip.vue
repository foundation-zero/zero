<script setup lang="ts">
import { Button } from "@/components/ui/button/index.ts";
import { formatInt, ratioAsPercentage, tScoped } from "@/modules/common/lib/utils.ts";
import {
  BoilerTankState,
  ControlComponentType,
  ParametersType,
  SensorComponentType,
} from "@/modules/thrs/types/index.ts";
import { computed } from "vue";
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
  TooltipListItemValveState,
} from "../../components/tooltip-list";
import { MimicComponentType } from "../../types";
import { BOILER_TANK_CAPACITY } from "../../utils/consts.ts";
import { BoilerTankMode } from "../components/boiler-tank/index.ts";
import { HeatPumpMode, HeatPumpModes } from "../components/heat-pump/index.ts";
import BoilerTankInstance from "../instances/BoilerTankInstance.vue";
import { getField, getMimicDataProvider } from "../providers/index.ts";

const props = defineProps<TooltipComponentContext<MimicComponentType.BoilerTank>>();

const tUnits = tScoped("units");
const tSources = tScoped("thrapp.tooltips.sources");
const tLabels = tScoped("thrapp.tooltips.labels");
const tItems = tScoped("thrapp.tooltips.items");

const { getSensorValue, getParameterValue, getControlValue } = getMimicDataProvider();

const currentTemperature = getSensorValue(props.sensors.temperature);

const boostingSupply = getField(
  SensorComponentType.Temperature,
  "boilers",
  "boilersTemperatureBoostingSupply",
);
const boostingSupplyValue = getSensorValue(boostingSupply);

const minimumTemperature = getParameterValue(
  getField(ParametersType.Temperature, "boilers", "minimumTankTemperature"),
);
const maximumTemperature = getParameterValue(
  getField(ParametersType.Temperature, "boilers", "maximumTankTemperature"),
);

const currentLevel = getSensorValue(props.sensors.level);
const currentLevelPercentage = ratioAsPercentage(
  computed(() => (currentLevel.value?.level.value ?? 0) / BOILER_TANK_CAPACITY),
);
const minimumLevel = getParameterValue(
  getField(ParametersType.Level, "boilers", "minimumTankLevel"),
);
const maximumLevel = getParameterValue(
  getField(ParametersType.Level, "boilers", "maximumTankLevel"),
);

const controller = getControlValue(
  getField(ControlComponentType.BoilersTanksController, "boilers", "boilersTanksController"),
);
const boilerState = computed(() => controller.value?.[props.custom.tankStateField].value);
</script>

<template>
  <MimicTooltip>
    <BoilerTankInstance v-bind="props" />

    <TooltipList class="border-b-0">
      <TooltipListItem size="sm">
        <TooltipListItemTitle>{{ tItems("itemName") }}</TooltipListItemTitle>
        <TooltipListItemTitle>{{ tooltip?.itemName }}</TooltipListItemTitle>
      </TooltipListItem>
      <TooltipListItem size="sm">
        <TooltipListItemTitle>{{ tItems("technicalName") }}</TooltipListItemTitle>
        <TooltipListItemTitle>{{ tooltip?.technicalName }}</TooltipListItemTitle>
      </TooltipListItem>
      <TooltipListItem class="mt-3">
        <TooltipListItemTitle class="text-muted-foreground text-xs">
          {{ tItems("automatedControl") }}
        </TooltipListItemTitle>
        <Button size="sm">{{ tLabels("controlManually") }}</Button>
      </TooltipListItem>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ tLabels("input") }}</TooltipListHeader>
      <TooltipListItem>
        <TooltipListItemTitle>
          {{ tItems("state") }}
          <TooltipListItemSource external>{{ tSources("tankState") }}</TooltipListItemSource>
        </TooltipListItemTitle>
        <BoilerTankMode :mode="boilerState" />
      </TooltipListItem>
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>{{ tLabels("output") }}</TooltipListHeader>
      <TooltipListItem>
        <TooltipListItemTitle>{{ tItems("temperature") }}</TooltipListItemTitle>
        <TooltipListItemValue>On temperature</TooltipListItemValue>
      </TooltipListItem>
      <TooltipListItem size="sm">
        <TooltipListItemTitle>
          {{ tItems("currentTemperature") }}
          <TooltipListItemSource :source="sensors.temperature" />
        </TooltipListItemTitle>
        <TooltipListItemNumber
          :value="currentTemperature?.temperature.value"
          :unit="tUnits('celsius')"
          :format="formatInt"
        />
      </TooltipListItem>
      <TooltipListItem size="sm">
        <TooltipListItemTitle>
          {{ tItems("incomingTemperature") }}
          <TooltipListItemSource :source="boostingSupply" />
        </TooltipListItemTitle>
        <TooltipListItemNumber
          :value="boostingSupplyValue?.temperature.value"
          :unit="tUnits('celsius')"
          :format="formatInt"
        />
      </TooltipListItem>
      <TooltipListItem size="sm">
        <TooltipListItemTitle>
          {{ tItems("minTemperature") }}
          <TooltipListItemSource url>{{ tSources("minTemperature") }}</TooltipListItemSource>
        </TooltipListItemTitle>
        <TooltipListItemNumber
          :value="minimumTemperature"
          :unit="tUnits('celsius')"
          :format="formatInt"
        />
      </TooltipListItem>
      <TooltipListItem size="sm">
        <TooltipListItemTitle>
          {{ tItems("maxTemperature") }}
          <TooltipListItemSource url>{{ tSources("maxTemperature") }}</TooltipListItemSource>
        </TooltipListItemTitle>
        <TooltipListItemNumber
          :value="maximumTemperature"
          :unit="tUnits('celsius')"
          :format="formatInt"
        />
      </TooltipListItem>
      <TooltipListItem>
        <TooltipListItemTitle>{{ tItems("filling") }}</TooltipListItemTitle>
        <TooltipListItemNumber
          :value="currentLevelPercentage"
          :unit="tUnits('percent')"
          :format="formatInt"
          dense
        />
      </TooltipListItem>
      <TooltipListItem size="sm">
        <TooltipListItemTitle>
          {{ tItems("levelSensor") }}
          <TooltipListItemSource :source="sensors.level" />
        </TooltipListItemTitle>
        <TooltipListItemValue>Not empty</TooltipListItemValue>
      </TooltipListItem>
      <TooltipListItem size="sm">
        <TooltipListItemTitle>
          {{ tItems("fill") }}
          <TooltipListItemSource :source="sensors.level" />
        </TooltipListItemTitle>
        <TooltipListItemNumber
          :value="currentLevel?.level.value"
          :format="formatInt"
          :unit="tUnits('liters')"
        />
      </TooltipListItem>
      <TooltipListItem size="sm">
        <TooltipListItemTitle>
          {{ tItems("capacity") }}
          <TooltipListItemSource>{{ tSources("capacity") }}</TooltipListItemSource>
        </TooltipListItemTitle>
        <TooltipListItemNumber
          :value="BOILER_TANK_CAPACITY"
          :format="formatInt"
          :unit="tUnits('liters')"
        />
      </TooltipListItem>
      <TooltipListItem size="sm">
        <TooltipListItemTitle>
          {{ tItems("minLevel") }}
          <TooltipListItemSource url>{{ tSources("minLevel") }}</TooltipListItemSource>
        </TooltipListItemTitle>
        <TooltipListItemNumber
          :value="minimumLevel"
          :format="formatInt"
          :unit="tUnits('liters')"
        />
      </TooltipListItem>
      <TooltipListItem size="sm">
        <TooltipListItemTitle>
          {{ tItems("maxLevel") }}
          <TooltipListItemSource url>{{ tSources("maxLevel") }}</TooltipListItemSource>
        </TooltipListItemTitle>
        <TooltipListItemNumber
          :value="maximumLevel"
          :format="formatInt"
          :unit="tUnits('liters')"
        />
      </TooltipListItem>
      <TooltipListItem v-if="boilerState === BoilerTankState.Filling">
        <TooltipListItemTitle>{{ tItems("estimatedFillingTime") }}</TooltipListItemTitle>
        <TooltipListItemTimeRemaining :value="controller?.timeToFill.value" />
      </TooltipListItem>
      <!-- <TooltipListItem>
        <TooltipListItemTitle>{{ items("estimatedTimeToHeat") }}</TooltipListItemTitle>
        <TooltipListItemTimeRemaining :value="0" />
      </TooltipListItem> -->
    </TooltipList>

    <TooltipList>
      <TooltipListHeader>
        {{ tLabels("controls") }}
        <TooltipListItemAction>{{ tLabels("viewControls") }}</TooltipListItemAction>
      </TooltipListHeader>
      <TooltipListItem>
        <TooltipListItemTitle>{{ tItems("tankController") }}</TooltipListItemTitle>
        <HeatPumpMode :mode="HeatPumpModes.Active" />
      </TooltipListItem>
      <TooltipListItem size="sm">
        <TooltipListItemTitle>
          {{ tItems("tank1") }}
          <TooltipListItemSource external>1053</TooltipListItemSource>
          <TooltipListItemSource url>{{ tSources("tank1") }}</TooltipListItemSource>
        </TooltipListItemTitle>
        <BoilerTankMode :mode="controller?.tank1State.value" />
      </TooltipListItem>
      <TooltipListItem size="sm">
        <TooltipListItemTitle>
          {{ tItems("tank2") }}
          <TooltipListItemSource external>1054</TooltipListItemSource>
          <TooltipListItemSource url>{{ tSources("tank2") }}</TooltipListItemSource>
        </TooltipListItemTitle>
        <BoilerTankMode :mode="controller?.tank2State.value" />
      </TooltipListItem>
      <TooltipListItem size="sm">
        <TooltipListItemTitle>
          {{ tItems("tank3") }}
          <TooltipListItemSource external>1055</TooltipListItemSource>
          <TooltipListItemSource url>{{ tSources("tank3") }}</TooltipListItemSource>
        </TooltipListItemTitle>
        <BoilerTankMode :mode="controller?.tank3State.value" />
      </TooltipListItem>
      <TooltipListItem size="sm">
        <TooltipListItemTitle>
          {{ tItems("boostReturnValve") }}
          <TooltipListItemSource :source="sensors.boostReturnValve" />
        </TooltipListItemTitle>
        <TooltipListItemValveState :source="sensors.boostReturnValve" />
      </TooltipListItem>
      <TooltipListItem size="sm">
        <TooltipListItemTitle>
          {{ tItems("boostSupplyValve") }}
          <TooltipListItemSource :source="sensors.boostSupplyValve" />
        </TooltipListItemTitle>
        <TooltipListItemValveState :source="sensors.boostSupplyValve" />
      </TooltipListItem>
      <TooltipListItem size="sm">
        <TooltipListItemTitle>
          {{ tItems("supplyValve") }}
          <TooltipListItemSource :source="sensors.supplyValve" />
        </TooltipListItemTitle>
        <TooltipListItemValveState :source="sensors.supplyValve" />
      </TooltipListItem>
      <TooltipListItem size="sm">
        <TooltipListItemTitle>
          {{ tItems("dischargeValve") }}
          <TooltipListItemSource :source="sensors.dischargeValve" />
        </TooltipListItemTitle>
        <TooltipListItemValveState :source="sensors.dischargeValve" />
      </TooltipListItem>
    </TooltipList>
  </MimicTooltip>
</template>
