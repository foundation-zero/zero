<script setup lang="ts">
import {
  COLUMN_GROUP_ATTRIBUTE,
  COLUMN_ITEM_ATTRIBUTE,
  useColumnSegments,
} from "@/modules/common/lib/columns";
import { cn, tScoped } from "@/modules/common/lib/utils";
import {
  type Component,
  computed,
  defineAsyncComponent,
  type HTMLAttributes,
  useTemplateRef,
} from "vue";
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
      {
        key: MimicComponentType.ManualPump,
        item: defineAsyncComponent(() => import("./items/ManualPump.vue")),
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
];

const groups = computed(() =>
  GROUPS.map((group) => ({
    ...group,
    entries: group.entries.filter(({ key, subType }) =>
      isInLegend(props.legend, key, subType as never),
    ),
  })).filter((group) => group.entries.length > 0),
);

// Groups may continue in the next column; each column a group spans becomes a segment that starts
// with a (repeated) header.
const container = useTemplateRef<HTMLElement>("container");
const segments = useColumnSegments(
  container,
  computed(() => groups.value.map(({ title, entries }) => ({ key: title, items: entries }))),
);
</script>

<template>
  <!--
    Groups may continue in the next column so the columns stay balanced. Items never split, and each
    segment of a group starts with the header in one block with its first item, so a header never
    ends up alone at a column bottom and is repeated at the top of a continued column.
  -->
  <div
    ref="container"
    :class="cn('gap-x-4 md:columns-2 xl:columns-3 [&_li]:break-inside-avoid', props.class)"
  >
    <Legend
      v-for="group in segments"
      :key="group.key"
      v-bind="{ [COLUMN_GROUP_ATTRIBUTE]: group.key }"
    >
      <template
        v-for="(segment, index) in group.segments"
        :key="index"
      >
        <div class="break-inside-avoid">
          <LegendGroupHeader class="flex items-baseline justify-between gap-2">
            {{ t(`groups.${group.key}`) }}
            <span
              v-if="group.segments.length > 1"
              class="text-muted-foreground text-sm font-normal"
            >
              {{ index + 1 }}/{{ group.segments.length }}
            </span>
          </LegendGroupHeader>
          <LegendGroup :class="['gap-2', { 'border-b-0 pb-0': segment.length > 1 }]">
            <component
              :is="segment[0].item"
              v-bind="{ [COLUMN_ITEM_ATTRIBUTE]: true }"
              :class="{ 'w-full': group.key === 'connectingCircuits' }"
            />
          </LegendGroup>
        </div>
        <LegendGroup
          v-if="segment.length > 1"
          class="gap-2 border-t-0 pt-2"
        >
          <component
            :is="entry.item"
            v-for="entry in segment.slice(1)"
            :key="`${entry.key}-${entry.subType ?? ''}`"
            v-bind="{ [COLUMN_ITEM_ATTRIBUTE]: true }"
            :class="{ 'w-full': group.key === 'connectingCircuits' }"
          />
        </LegendGroup>
      </template>
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
