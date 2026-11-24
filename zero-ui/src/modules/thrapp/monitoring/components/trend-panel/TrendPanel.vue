<script setup lang="ts">
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { tScoped } from "@/modules/common/lib/utils";
import { type MonitoringMetric, PANEL_GRID } from "@/modules/thrapp/monitoring/monitoring.consts";
import {
  type Timeline,
  useMonitoringSeries,
} from "@/modules/thrapp/monitoring/monitoring-data.utils";
import type {
  TotalRow,
  ChartOverlay,
  ResolvedRange,
  SignalStates,
  TrendPanelConfig,
} from "@/modules/thrapp/monitoring/monitoring.types";
import {
  seriesColor,
  useStateStyles,
  useThemeMode,
} from "@/modules/thrapp/monitoring/monitoring.utils";
import { computed, ref, useTemplateRef } from "vue";
import { LatestValuesTable } from "../latest-values-table";
import { styledSegments } from "../state-panel";
import { HeatDistribution } from "../heat-distribution";
import { TotalsTable } from "../totals-table";
import { TrendChart, type TrendKind } from "../trend-chart";
import {
  stackable,
  energyRows,
  latestRows,
  legendGroups,
  sortedMetrics,
  trendLimit,
  trendLines,
  litres,
  waterFlows,
} from "./trend-panel.utils";

/** A trend chart for one of the panel's metrics, with the latest values beside it. */
const props = defineProps<{
  config: TrendPanelConfig;
  /** The module as the API names it. */
  module: string;
  timeline: Timeline;
  /** States of the module's signals, for the bands behind the lines. */
  states: SignalStates[];
  /** Charts in one group show the hovered time together. */
  group?: string;
}>();

const emit = defineEmits<{ zoom: [range: ResolvedRange] }>();

const t = tScoped("thrapp.monitoring");
const styleOf = useStateStyles();

const metric = ref<MonitoringMetric>(props.config.defaultMetric ?? props.config.metrics[0]);
const metricOptions = computed(() =>
  sortedMetrics(props.config.metrics, (option) => t(`metrics.${option}`)),
);

const { data, loading, error } = useMonitoringSeries(props.timeline, () => ({
  module: props.module,
  // Water needs all its metrics at once; other panels show the one picked.
  metrics: [
    ...(props.config.display === "water" ? props.config.metrics : [metric.value]),
    ...(props.config.limits ? [props.config.limits.lower, props.config.limits.upper] : []),
  ],
  devices: props.config.devices,
}));

const unit = computed(() => data.value.find((series) => series.metric === metric.value)?.unit);
const display = computed(() => props.config.display ?? "line");
const water = computed(() =>
  display.value === "water"
    ? waterFlows(
        data.value,
        props.config.devices?.[0] ?? "",
        props.config.devices?.slice(1) ?? [],
        props.timeline.resolved.value,
      )
    : undefined,
);
const lines = computed(() => {
  if (water.value)
    return [
      { name: t("water.in"), device: "in", points: water.value.inflow },
      { name: t("water.out"), device: "out", points: water.value.outflow },
    ];
  const raw = trendLines(data.value, metric.value, props.config);
  return display.value === "heat" ? stackable(raw) : raw;
});
const CHART_KIND = {
  line: "line",
  heat: "stacked",
  distribution: "stacked",
  water: "area",
} as const satisfies Record<string, TrendKind>;
const chartUnit = computed(() => (water.value ? "L/min" : unit.value));
const groups = computed(() => legendGroups(lines.value, props.config, (key) => t(`groups.${key}`)));
const root = useTemplateRef<HTMLElement>("root");
const { mode } = useThemeMode(root);
// The same colour per asset as its line in the chart.
const rows = computed(() => {
  const names = lines.value.map((line) => line.name);
  return latestRows(data.value, metric.value, props.config).map((row) => ({
    ...row,
    ...seriesColor(row.asset, names, mode.value),
  }));
});
const totals = computed<TotalRow[]>(() => {
  const names = lines.value.map((line) => line.name);
  const colour = (row: TotalRow) => ({ ...row, ...seriesColor(row.asset, names, mode.value) });
  if (!water.value) return energyRows(data.value, metric.value, props.config).map(colour);
  const { inflow, outflow, period } = water.value;
  const [came, went] = [litres(inflow, period), litres(outflow, period)];
  return [
    colour({ asset: t("water.in"), value: came }),
    colour({ asset: t("water.out"), value: went }),
    { asset: t("water.net"), value: came - went, derived: true },
  ];
});
const totalsUnit = computed(() => (water.value ? "L" : "kWh"));

const limits = computed(() => {
  const config = props.config.limits;
  if (!config) return {};
  return {
    lower: trendLimit(data.value, config.lower, t(`metrics.${config.lower}`)),
    upper: trendLimit(data.value, config.upper, t(`metrics.${config.upper}`)),
  };
});
const overlays = computed<ChartOverlay[]>(() =>
  (props.config.overlays ?? []).map(({ signal, shown }) => ({
    key: signal,
    label: t(`chart.overlays.${signal}`),
    shown,
    bands: styledSegments(signal, props.states, styleOf).map(({ label, mode, start, end }) => ({
      label,
      mode,
      start,
      end,
    })),
  })),
);
</script>

<template>
  <div
    ref="root"
    class="flex flex-col gap-3"
  >
    <Select
      v-if="display === 'line' && props.config.metrics.length > 1"
      v-model="metric"
    >
      <SelectTrigger
        class="bg-background border-border h-10 w-[270px] rounded-sm text-sm font-medium"
        :aria-label="t('chart.metric')"
      >
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        <SelectItem
          v-for="option in metricOptions"
          :key="option"
          :value="option"
        >
          {{ t(`metrics.${option}`) }}
        </SelectItem>
      </SelectContent>
    </Select>
    <HeatDistribution
      v-if="display === 'distribution'"
      :rows="totals"
      unit="kWh"
      :loading="loading"
      :error="error"
    />
    <div
      v-else
      :class="PANEL_GRID"
    >
      <TrendChart
        :lines="lines"
        :range="props.timeline.resolved.value"
        :unit="chartUnit"
        :overlays="overlays"
        :limits="limits"
        :legend-groups="groups"
        :kind="CHART_KIND[display]"
        :bin-width="water?.period"
        :group="props.group"
        :storage-key="`${props.module}:${props.config.key}`"
        :loading="loading"
        :error="error"
        @zoom="emit('zoom', $event)"
      >
        <template #overlay="slotProps">
          <slot
            name="overlay"
            v-bind="slotProps"
          />
        </template>
      </TrendChart>
      <TotalsTable
        v-if="display !== 'line'"
        :title="t(`totals.${display}.title`)"
        :asset-header="t(`totals.${display}.asset`)"
        :value-header="t(`totals.${display}.value`)"
        :unit="totalsUnit"
        :rows="totals"
        :shares="!water"
        :sum="!water"
      />
      <LatestValuesTable
        v-else
        :rows="rows"
        :value-header="t(`metrics.${metric}`)"
        :unit="unit"
        :totals="props.config.totals"
      />
    </div>
  </div>
</template>
