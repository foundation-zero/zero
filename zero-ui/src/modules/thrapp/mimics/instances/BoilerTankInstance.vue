<script setup lang="ts">
import { BoilerTankState, ControllerStateComponentType } from "@/modules/thrs/types";
import { computed } from "vue";
import { MimicComponentInstanceProps } from ".";
import { MimicTooltipTrigger, TooltipComponentContext } from "../../components/tooltip";
import { MimicComponentType } from "../../types";
import { BoilerTank, BoilerTankMode, BoilerTankTitle } from "../components/boiler-tank";
import {
  ValueList,
  ValueListFillLevelItem,
  ValueListTemperatureItem,
  ValueListTimeItem,
} from "../components/value-list";
import YardTag from "../components/yard-tag/YardTag.vue";
import { getField, getMimicDataProvider } from "../providers";

const props = defineProps<
  MimicComponentInstanceProps & {
    width?: number | string;
    height?: number | string;
    forceHeight?: boolean;
  } & TooltipComponentContext<MimicComponentType.BoilerTank>
>();

const { getSensorValue, getComponentState, getControllerState } = getMimicDataProvider();

const level = getSensorValue(props.sensors.level);
const fillLevel = computed(() => (level.value?.level.value ?? 0) / 275);

const state = getComponentState();

const controller = getControllerState(
  getField(ControllerStateComponentType.DhwTanksController, "dhw", "dhwTanksController"),
);
const mode = computed(() => controller.value?.[props.custom.tankStateField].value);
const fillTime = computed(() => controller.value?.timeToFill.value);
</script>

<template>
  <MimicTooltipTrigger
    :type="MimicComponentType.BoilerTank"
    :data="props"
  >
    <BoilerTank
      :force-height="forceHeight"
      :width="width"
      :height="height"
      :x="x"
      :y="y"
      :level="fillLevel"
      :mode="mode"
      :state="state"
    >
      <YardTag>{{ tooltip?.yardTag }}</YardTag>
      <BoilerTankTitle>{{ tooltip?.title }}</BoilerTankTitle>
      <BoilerTankMode
        :mode="mode"
        :state="state"
      />
      <ValueList class="gap-0">
        <ValueListTemperatureItem :source="sensors.temperature" />
        <ValueListFillLevelItem
          :source="sensors.level"
          :max-level="275"
        />
        <ValueListTimeItem
          v-if="mode === BoilerTankState.Filling"
          :value="fillTime"
        />
      </ValueList>
    </BoilerTank>
    <slot />
  </MimicTooltipTrigger>
</template>
