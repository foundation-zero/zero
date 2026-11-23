<script setup lang="ts">
import { Switch } from "@/components/ui/switch";
import { tScoped } from "@/modules/common/lib/utils";
import { MODE_COLORS } from "@/modules/thrapp/mimics/components/mode-badge/mode-badge.consts";
import { LIMIT_COLOR, PLOT_INSET } from "@/modules/thrapp/monitoring/monitoring.consts";
import type {
  ChartOverlay,
  LegendGroup,
  ResolvedRange,
  TrendLimit,
  TrendLine,
} from "@/modules/thrapp/monitoring/monitoring.types";
import {
  seriesColor,
  useCssColors,
  usePlotDrag,
} from "@/modules/thrapp/monitoring/monitoring.utils";
import { useElementSize, useLocalStorage } from "@vueuse/core";
import { LineChart } from "echarts/charts";
import { GridComponent, MarkAreaComponent, TooltipComponent } from "echarts/components";
import { connect, use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { computed, ref, useTemplateRef } from "vue";
import VChart from "vue-echarts";
import {
  PLOT_BOTTOM,
  PLOT_TOP,
  showGroup,
  toggleShown,
  type TrendKind,
  trendOption,
} from "./trend-chart.utils";

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, MarkAreaComponent]);

/**
 * Lines per device over the shared range, with modes as faint bands behind them
 * and optional stepped limits. A legend click shows only that line, further
 * clicks add or remove lines; drag across the plot to zoom.
 */
const props = withDefaults(
  defineProps<{
    lines: TrendLine[];
    range: ResolvedRange;
    unit?: string | null;
    overlays?: ChartOverlay[];
    limits?: { lower?: TrendLimit; upper?: TrendLimit };
    legendGroups?: LegendGroup[];
    kind?: TrendKind;
    /** Width in ms of the period each point averages, named in the tooltip. */
    binWidth?: number;
    /** Charts in one group show the hovered time together. */
    group?: string;
    /** Remembers per viewer which overlays are shown. */
    storageKey?: string;
    loading?: boolean;
    error?: string;
  }>(),
  {
    storageKey: undefined,
    unit: null,
    overlays: () => [],
    limits: () => ({}),
    legendGroups: () => [],
    kind: "line",
    binWidth: undefined,
    group: undefined,
    loading: false,
    error: undefined,
  },
);

const emit = defineEmits<{ zoom: [range: ResolvedRange] }>();

// Replace the whole option rather than merge series by index: merged series
// linger when lines are hidden, and an open tooltip then reads series that are gone.
const UPDATE_OPTIONS = { notMerge: true };

const t = tScoped("thrapp.monitoring");
const root = useTemplateRef<HTMLElement>("root");
const plot = useTemplateRef<HTMLElement>("plot");

const shownOverlays = props.storageKey
  ? useLocalStorage<Record<string, boolean>>(`thrs-monitoring-overlays:${props.storageKey}`, {})
  : ref<Record<string, boolean>>({});
const isShown = (overlay: ChartOverlay) => shownOverlays.value[overlay.key] ?? overlay.shown;
const setShown = (overlay: ChartOverlay, value: boolean) => {
  shownOverlays.value = { ...shownOverlays.value, [overlay.key]: value };
};

const allBands = computed(() => props.overlays.flatMap((overlay) => overlay.bands));
const { colors: resolved, mode } = useCssColors<string>(
  () => ({
    text: "var(--muted-foreground)",
    grid: "var(--border)",
    limit: LIMIT_COLOR,
    ...Object.fromEntries(
      allBands.value.map((band) => [`band:${band.mode}`, MODE_COLORS[band.mode]]),
    ),
  }),
  root,
);

const names = computed(() => props.lines.map((line) => line.name));
// Null shows every line.
const shownLines = ref<Set<string> | null>(null);
const hidden = computed(() => {
  const shown = shownLines.value;
  if (!shown || !names.value.some((name) => shown.has(name))) return new Set<string>();
  return new Set(names.value.filter((name) => !shown.has(name)));
});

const option = computed(() =>
  trendOption({
    lines: props.lines,
    hidden: hidden.value,
    layers: props.overlays
      .filter(isShown)
      .map((overlay, index) => ({ bands: overlay.bands, labelAt: index === 0 ? "top" : "bottom" })),
    limits: props.limits,
    range: props.range,
    unit: props.unit,
    mode: mode.value,
    kind: props.kind,
    binWidth: props.binWidth,
    totalLabel: t("chart.total"),
    colors: {
      text: resolved.value.text,
      grid: resolved.value.grid,
      limit: resolved.value.limit,
      bands: Object.fromEntries(
        allBands.value.map((band) => [band.mode, resolved.value[`band:${band.mode}`]]),
      ),
    },
  }),
);

type LegendItem = { name: string; color: string; dashed: boolean; hidden: boolean };
const item = (name: string): LegendItem => ({
  name,
  ...seriesColor(name, names.value, mode.value),
  hidden: hidden.value.has(name),
});
const legend = computed(() => {
  const present = new Set(names.value);
  const groups = props.legendGroups
    .map((group) => ({ ...group, names: group.names.filter((name) => present.has(name)) }))
    .filter((group) => group.names.length);
  const grouped = new Set(groups.flatMap((group) => group.names));
  const rest = names.value.filter((name) => !grouped.has(name));
  return [
    ...groups.map((group) => ({
      key: group.key,
      label: group.label,
      names: group.names,
      items: group.names.map(item),
      active: group.names.every((name) => !hidden.value.has(name)) && hidden.value.size > 0,
    })),
    ...(rest.length
      ? [{ key: "", label: "", names: rest, items: rest.map(item), active: false }]
      : []),
  ];
});
const hasGroups = computed(() => legend.value.some((row) => row.label));
const limitNames = computed(() =>
  [props.limits.lower, props.limits.upper].flatMap((limit) => (limit ? [limit.name] : [])),
);
const isEmpty = computed(() => props.lines.every((line) => !line.points.length));

const toggle = (name: string) => {
  shownLines.value = toggleShown(shownLines.value, name, names.value);
};
const isolateGroup = (groupNames: string[]) => {
  shownLines.value = showGroup(hidden.value.size ? shownLines.value : null, groupNames);
};

const { selection } = usePlotDrag(
  plot,
  () => props.range,
  PLOT_INSET,
  (range) => emit("zoom", range),
);

// A chart in a collapsed group has no place on the page; linked, it would still
// show the hovered time, with its tooltip in the corner of the window.
const { width: plotWidth } = useElementSize(plot);
const linkedGroup = computed(() => (plotWidth.value > 0 ? props.group : undefined));

const onReady = () => {
  if (props.group) connect(props.group);
};
</script>

<template>
  <div
    ref="root"
    class="border-border bg-background flex min-w-0 flex-col gap-3 rounded-lg border p-4"
  >
    <div
      v-if="props.overlays.length"
      class="font-ui text-muted-foreground -mb-2 flex flex-wrap justify-end gap-x-6 gap-y-2 text-sm font-medium"
    >
      <label
        v-for="overlay in props.overlays"
        :key="overlay.key"
        class="flex cursor-pointer items-center gap-2"
      >
        {{ overlay.label }}
        <Switch
          :model-value="isShown(overlay)"
          @update:model-value="setShown(overlay, $event)"
        />
      </label>
    </div>
    <div
      ref="plot"
      class="relative h-56 cursor-crosshair select-none lg:h-[352px]"
    >
      <VChart
        :option="option"
        :group="linkedGroup"
        :update-options="UPDATE_OPTIONS"
        :class="{ 'opacity-60': props.loading }"
        autoresize
        @rendered="onReady"
      />
      <p
        v-if="props.error || (isEmpty && !props.loading)"
        class="pointer-events-none absolute inset-0 flex items-center justify-center text-sm"
        :class="props.error ? 'text-destructive' : 'text-muted-foreground'"
      >
        {{ props.error ? t("chart.error", { message: props.error }) : t("chart.empty") }}
      </p>
      <slot
        name="overlay"
        :top="PLOT_TOP"
        :bottom="PLOT_BOTTOM"
      />
      <div
        v-if="selection"
        class="bg-primary/10 border-primary/50 pointer-events-none absolute border-x"
        :style="{
          left: `${selection.left}px`,
          width: `${selection.width}px`,
          top: `${PLOT_TOP}px`,
          bottom: `${PLOT_BOTTOM}px`,
        }"
      />
    </div>

    <div class="bg-dull font-ui rounded-sm px-3 py-2.5 text-sm">
      <div
        class="grid items-baseline gap-x-6 gap-y-2"
        :class="hasGroups ? 'grid-cols-[auto_minmax(0,1fr)]' : 'grid-cols-1'"
      >
        <template
          v-for="row in legend"
          :key="row.key"
        >
          <button
            v-if="hasGroups"
            type="button"
            :disabled="!row.label"
            class="text-muted-foreground hover:text-foreground text-left text-xs font-semibold tracking-wide whitespace-nowrap uppercase disabled:pointer-events-none"
            :class="{ 'text-foreground': row.active }"
            :title="t('chart.showGroup', { group: row.label })"
            @click="isolateGroup(row.names)"
          >
            {{ row.label }}
          </button>
          <div class="flex flex-wrap items-center gap-x-4 gap-y-1.5">
            <button
              v-for="entry in row.items"
              :key="entry.name"
              type="button"
              class="text-foreground hover:bg-background/60 -mx-1 flex items-center gap-2 rounded-xs px-1 font-medium"
              :class="{ 'opacity-40': entry.hidden }"
              :aria-pressed="!entry.hidden"
              @click="toggle(entry.name)"
            >
              <svg
                width="18"
                height="4"
                aria-hidden="true"
              >
                <line
                  x1="0"
                  y1="2"
                  x2="18"
                  y2="2"
                  stroke-width="2.5"
                  stroke-linecap="round"
                  :stroke="entry.color"
                  :stroke-dasharray="entry.dashed ? '4 3' : undefined"
                />
              </svg>
              {{ entry.name }}
            </button>
          </div>
        </template>
        <div
          v-if="limitNames.length || hidden.size"
          class="col-span-full flex flex-wrap items-center gap-x-4 gap-y-1.5"
        >
          <span
            v-for="name in limitNames"
            :key="name"
            class="text-muted-foreground flex items-center gap-2 font-medium"
          >
            <svg
              width="18"
              height="4"
              aria-hidden="true"
            >
              <line
                x1="0"
                y1="2"
                x2="18"
                y2="2"
                stroke-width="1.5"
                stroke-dasharray="3 2"
                :style="{ stroke: LIMIT_COLOR }"
              />
            </svg>
            {{ name }}
          </span>
          <button
            v-if="hidden.size"
            type="button"
            class="text-primary font-semibold underline-offset-2 hover:underline"
            @click="shownLines = null"
          >
            {{ t("chart.showAll") }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
