<script setup lang="ts">
import { cn, tScoped } from "@/modules/common/lib/utils";
import { type Component, computed, defineAsyncComponent, type HTMLAttributes } from "vue";
import { ManualValveType } from "../../mimics/components/manual-valve";
import { MimicComponentType } from "../../types";
import { Legend, LegendGroup, LegendGroupHeader } from "../legend";
import Arrow from "./items/Arrow.vue";
import LabelTag from "./items/LabelTag.vue";
import LabelValue from "./items/LabelValue.vue";
import Pipe from "./items/Pipe.vue";
import SectionArea from "./items/SectionArea.vue";
import { isInLegend, LegendFeature, LegendKey, LegendMap, LegendSubType } from "./map";

const props = defineProps<{ legend: LegendMap; class?: HTMLAttributes["class"] }>();
const t = tScoped("thrapp.legends");

type LegendEntry = {
  [Key in LegendKey]: {
    key: Key;
    subType?: Key extends keyof LegendSubType ? LegendSubType[Key][number] : never;
    item: Component;
  };
}[LegendKey];

const GROUPS: { title: string; entries: LegendEntry[] }[] = [
  {
    title: "connectingCircuits",
    entries: [
      {
        key: MimicComponentType.ExchangeCircuit,
        item: defineAsyncComponent(() => import("./items/OtherMimic.vue")),
      },
      {
        key: MimicComponentType.ConnectingCircuit,
        item: defineAsyncComponent(() => import("./items/ConnectingCircuit.vue")),
      },
      {
        key: MimicComponentType.FreshwaterCircuit,
        item: defineAsyncComponent(() => import("./items/FreshwaterCircuit.vue")),
      },
      {
        key: MimicComponentType.SeawaterCircuit,
        item: defineAsyncComponent(() => import("./items/SeawaterCircuit.vue")),
      },
    ],
  },
  {
    title: "assets",
    entries: [
      {
        key: MimicComponentType.HeatPump,
        item: defineAsyncComponent(() => import("./items/HeatPump.vue")),
      },
      {
        key: MimicComponentType.HVAC,
        item: defineAsyncComponent(() => import("./items/HVAC.vue")),
      },
      {
        key: MimicComponentType.BoilerTank,
        item: defineAsyncComponent(() => import("./items/BoilerTank.vue")),
      },
      { key: MimicComponentType.Pvt, item: defineAsyncComponent(() => import("./items/Pvt.vue")) },
      { key: MimicComponentType.Pcm, item: defineAsyncComponent(() => import("./items/Pcm.vue")) },
      {
        key: MimicComponentType.Thruster,
        item: defineAsyncComponent(() => import("./items/Thruster.vue")),
      },
      {
        key: MimicComponentType.DcConverter,
        item: defineAsyncComponent(() => import("./items/DcConverter.vue")),
      },
      {
        key: MimicComponentType.PropulsionDrive,
        item: defineAsyncComponent(() => import("./items/PropulsionDrive.vue")),
      },
      {
        key: MimicComponentType.PropulsionCooler,
        item: defineAsyncComponent(() => import("./items/PropulsionCooler.vue")),
      },
      {
        key: MimicComponentType.ShorePowerConverter,
        item: defineAsyncComponent(() => import("./items/ShorePowerConverter.vue")),
      },
      {
        key: MimicComponentType.ExpansionTank,
        item: defineAsyncComponent(() => import("./items/ExpansionTank.vue")),
      },
      {
        key: MimicComponentType.AirTrapVessel,
        item: defineAsyncComponent(() => import("./items/AirTrapVessel.vue")),
      },
    ],
  },
  {
    title: "actuatedValveComponents",
    entries: [
      {
        key: MimicComponentType.SwitchValve,
        item: defineAsyncComponent(() => import("./items/SwitchValves.vue")),
      },
      {
        key: MimicComponentType.FlowControlValve,
        item: defineAsyncComponent(() => import("./items/FlowValve.vue")),
      },
      {
        key: MimicComponentType.MixValve,
        item: defineAsyncComponent(() => import("./items/MixValve.vue")),
      },
      {
        key: MimicComponentType.ThreeWaySwitchValve,
        item: defineAsyncComponent(() => import("./items/ThreeWaySwitchValve.vue")),
      },
    ],
  },
  {
    title: "heatExchangers",
    entries: [
      {
        key: MimicComponentType.HeatExchanger,
        item: defineAsyncComponent(() => import("./items/PlateHeatExchanger.vue")),
      },
    ],
  },
  {
    title: "pumps",
    entries: [
      {
        key: MimicComponentType.Pump,
        item: defineAsyncComponent(() => import("./items/Pumps.vue")),
      },
      {
        key: MimicComponentType.ManualPump,
        item: defineAsyncComponent(() => import("./items/ManualPump.vue")),
      },
    ],
  },
  {
    title: "sensors",
    entries: [
      {
        key: MimicComponentType.TemperatureSensor,
        item: defineAsyncComponent(() => import("./items/TemperatureSensors.vue")),
      },
      {
        key: MimicComponentType.FlowSensor,
        item: defineAsyncComponent(() => import("./items/FlowSensors.vue")),
      },
      {
        key: MimicComponentType.PressureSensor,
        item: defineAsyncComponent(() => import("./items/PressureSensors.vue")),
      },
      {
        key: MimicComponentType.LevelSensor,
        item: defineAsyncComponent(() => import("./items/LevelSensors.vue")),
      },
      {
        key: MimicComponentType.LevelSwitch,
        item: defineAsyncComponent(() => import("./items/LevelSwitches.vue")),
      },
      {
        key: MimicComponentType.Pyranometer,
        item: defineAsyncComponent(() => import("./items/Pyranometer.vue")),
      },
    ],
  },
  {
    title: "manualComponents",
    entries: [
      {
        key: MimicComponentType.ManualValve,
        subType: ManualValveType.Switch,
        item: defineAsyncComponent(() => import("./items/ManualSwitchValve.vue")),
      },
      {
        key: MimicComponentType.ManualValve,
        subType: ManualValveType.FlowControl,
        item: defineAsyncComponent(() => import("./items/ManualFlowControlValve.vue")),
      },
      {
        key: MimicComponentType.ManualValve,
        subType: ManualValveType.ThreeWay,
        item: defineAsyncComponent(() => import("./items/ManualThreeWayValve.vue")),
      },
      {
        key: MimicComponentType.ManualValve,
        subType: ManualValveType.Flow,
        item: defineAsyncComponent(() => import("./items/ManualFlowValve.vue")),
      },
      {
        key: MimicComponentType.PressureGauge,
        item: defineAsyncComponent(() => import("./items/PressureGauges.vue")),
      },
      {
        key: MimicComponentType.CheckValve,
        item: defineAsyncComponent(() => import("./items/CheckValves.vue")),
      },
      {
        key: MimicComponentType.ExpansionValve,
        item: defineAsyncComponent(() => import("./items/ExpansionValve.vue")),
      },
    ],
  },
];

const groups = computed(() =>
  GROUPS.map((group) => ({
    ...group,
    entries: group.entries.filter(({ key, subType }) =>
      isInLegend(props.legend, key, subType as never),
    ),
  })).filter((group) => group.entries.length > 0),
);
</script>

<template>
  <div :class="cn('gap-x-4 md:columns-2 xl:columns-3', props.class)">
    <Legend
      v-for="group in groups"
      :key="group.title"
      class="break-inside-avoid"
    >
      <LegendGroupHeader>{{ t(`groups.${group.title}`) }}</LegendGroupHeader>
      <LegendGroup class="gap-2">
        <component
          :is="entry.item"
          v-for="entry in group.entries"
          :key="`${entry.key}-${entry.subType ?? ''}`"
          :class="{ 'w-full': group.title === 'connectingCircuits' }"
        />
      </LegendGroup>
    </Legend>

    <Legend class="break-inside-avoid">
      <LegendGroupHeader>{{ t("groups.pipes") }}</LegendGroupHeader>
      <LegendGroup>
        <Pipe class="border-flows-pipe">{{ t("pipes.pipe") }}</Pipe>
        <Pipe class="border-flows-pipe border-dashed">{{ t("pipes.connectingCircuitPipe") }}</Pipe>
        <template v-if="isInLegend(legend, LegendFeature.AnimatedFlows)">
          <Pipe class="border-flows-use-medium border-2">{{ t("pipes.inUseFlow") }}</Pipe>
          <Pipe class="border-flows-fill-medium border-2">{{ t("pipes.fillingFlow") }}</Pipe>
          <Pipe class="border-flows-heat-medium border-2">{{ t("pipes.heatingFlow") }}</Pipe>
        </template>
        <Pipe>
          <template #pipe>
            <Arrow />
          </template>
          {{ t("pipes.directionArrow") }}
        </Pipe>
      </LegendGroup>
    </Legend>

    <Legend class="break-inside-avoid">
      <LegendGroupHeader>{{ t("groups.labels") }}</LegendGroupHeader>
      <LegendGroup class="gap-2">
        <LabelTag />
        <LabelValue />
        <SectionArea v-if="isInLegend(legend, LegendFeature.SectionArea)" />
      </LegendGroup>
    </Legend>
  </div>
</template>
