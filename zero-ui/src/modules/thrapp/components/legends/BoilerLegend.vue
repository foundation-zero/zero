<script setup lang="ts">
import { cn, tScoped } from "@/modules/common/lib/utils";
import { HTMLAttributes } from "vue";
import { Legend, LegendGroup, LegendGroupHeader } from "../legend";
import Arrow from "./items/Arrow.vue";
import BoilerTank from "./items/BoilerTank.vue";
import FlowSensors from "./items/FlowSensors.vue";
import FlowValve from "./items/FlowValve.vue";
import HeatPump from "./items/HeatPump.vue";
import HVAC from "./items/HVAC.vue";
import LabelTag from "./items/LabelTag.vue";
import LabelValue from "./items/LabelValue.vue";
import LevelSensors from "./items/LevelSwitches.vue";
import ManualSwitchValve from "./items/ManualSwitchValve.vue";
import OtherMimic from "./items/OtherMimic.vue";
import Pipe from "./items/Pipe.vue";
import PlateHeatExchanger from "./items/PlateHeatExchanger.vue";
import PressureGauges from "./items/PressureGauges.vue";
import PressureSensors from "./items/PressureSensors.vue";
import Pumps from "./items/Pumps.vue";
import SectionArea from "./items/SectionArea.vue";
import SwitchValve from "./items/SwitchValves.vue";
import TemperatureSensors from "./items/TemperatureSensors.vue";

const props = defineProps<{ class?: HTMLAttributes["class"] }>();
const t = tScoped("thrapp.legends");
</script>

<template>
  <div :class="cn('grid sm:gap-x-4 md:grid-cols-2 xl:grid-cols-3', props.class)">
    <Legend>
      <LegendGroupHeader>{{ t("boilerLegend.groups.connectingCircuits") }}</LegendGroupHeader>
      <LegendGroup>
        <OtherMimic />
      </LegendGroup>
      <LegendGroupHeader>{{ t("boilerLegend.groups.assets") }}</LegendGroupHeader>
      <LegendGroup>
        <HeatPump />
        <HVAC />
        <BoilerTank />
      </LegendGroup>
      <LegendGroupHeader class="max-md:hidden xl:hidden">
        {{ t("boilerLegend.groups.actuatedValveComponents") }}
      </LegendGroupHeader>
      <LegendGroup class="max-md:hidden xl:hidden">
        <SwitchValve />
        <FlowValve />
      </LegendGroup>
      <LegendGroupHeader class="max-md:hidden xl:hidden">
        {{ t("boilerLegend.groups.heatExchangers") }}
      </LegendGroupHeader>
      <LegendGroup class="max-md:hidden xl:hidden">
        <PlateHeatExchanger />
      </LegendGroup>
    </Legend>

    <Legend class="md:max-xl:hidden">
      <LegendGroupHeader>{{ t("boilerLegend.groups.pumps") }}</LegendGroupHeader>
      <LegendGroup>
        <Pumps />
      </LegendGroup>
      <LegendGroupHeader>{{ t("boilerLegend.groups.actuatedValveComponents") }}</LegendGroupHeader>
      <LegendGroup>
        <SwitchValve />
        <FlowValve />
      </LegendGroup>
      <LegendGroupHeader>{{ t("boilerLegend.groups.heatExchangers") }}</LegendGroupHeader>
      <LegendGroup>
        <PlateHeatExchanger />
      </LegendGroup>
      <LegendGroupHeader>{{ t("boilerLegend.groups.sensors") }}</LegendGroupHeader>
      <LegendGroup class="gap-2">
        <TemperatureSensors />
        <FlowSensors />
        <PressureSensors />
        <LevelSensors />
      </LegendGroup>
    </Legend>

    <Legend>
      <LegendGroupHeader class="max-md:hidden xl:hidden">
        {{ t("boilerLegend.groups.pumps") }}
      </LegendGroupHeader>
      <LegendGroup class="max-md:hidden xl:hidden">
        <Pumps />
      </LegendGroup>
      <LegendGroupHeader class="max-md:hidden xl:hidden">
        {{ t("boilerLegend.groups.sensors") }}
      </LegendGroupHeader>
      <LegendGroup class="gap-2 max-md:hidden xl:hidden">
        <TemperatureSensors />
        <FlowSensors />
        <PressureSensors />
        <LevelSensors />
      </LegendGroup>
      <LegendGroupHeader>{{ t("boilerLegend.groups.manualComponents") }}</LegendGroupHeader>
      <LegendGroup>
        <ManualSwitchValve />
        <PressureGauges />
      </LegendGroup>
      <LegendGroupHeader>{{ t("boilerLegend.groups.pipes") }}</LegendGroupHeader>
      <LegendGroup>
        <Pipe class="border-flows-pipe">{{ t("pipes.pipe") }}</Pipe>
        <Pipe class="border-flows-pipe border-dashed">{{ t("pipes.connectingCircuitPipe") }}</Pipe>
        <Pipe class="border-flows-use-medium border-2">{{ t("pipes.inUseFlow") }}</Pipe>
        <Pipe class="border-flows-fill-medium border-2">{{ t("pipes.fillingFlow") }}</Pipe>
        <Pipe class="border-flows-heat-medium border-2">{{ t("pipes.heatingFlow") }}</Pipe>
        <Pipe>
          <template #pipe>
            <Arrow />
          </template>
          {{ t("pipes.directionArrow") }}
        </Pipe>
      </LegendGroup>
      <LegendGroupHeader>{{ t("boilerLegend.groups.labels") }}</LegendGroupHeader>
      <LegendGroup class="gap-2">
        <LabelTag />
        <LabelValue />
        <SectionArea />
      </LegendGroup>
    </Legend>
  </div>
</template>
