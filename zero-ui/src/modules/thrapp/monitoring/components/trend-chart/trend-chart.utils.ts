import { PLOT_INSET, TOOLTIP_CLASS } from "@/modules/thrapp/monitoring/monitoring.consts";
import type {
  ResolvedRange,
  TrendBand,
  TrendLimit,
  TrendLine,
} from "@/modules/thrapp/monitoring/monitoring.types";
import { heldUntil, limitRects, seriesColor } from "@/modules/thrapp/monitoring/monitoring.utils";
import type { EChartsOption, SeriesOption } from "echarts";

export type TrendColors = {
  text: string;
  grid: string;
  limit: string;
  bands: Record<string, string>;
};

/** How the lines are drawn: lines, areas stacked on each other, or filled lines. */
export type TrendKind = "line" | "stacked" | "area";

/** Bands of one signal; the bands of a second signal label at the bottom. */
export type BandLayer = { bands: TrendBand[]; labelAt: "top" | "bottom" };

export type TrendOptionInput = {
  lines: TrendLine[];
  hidden: Set<string>;
  layers: BandLayer[];
  limits: { lower?: TrendLimit; upper?: TrendLimit };
  range: ResolvedRange;
  unit: string | null;
  colors: TrendColors;
  mode: "light" | "dark";
  kind?: TrendKind;
  /** Width in ms of the period each point averages, named in the tooltip. */
  binWidth?: number;
  /** Label of the sum in the tooltip of stacked charts. */
  totalLabel?: string;
};

/** Replace the alpha of an rgba() colour. */
export const withAlpha = (rgba: string, alpha: number) =>
  rgba.replace(/rgba?\(([^,]+),([^,]+),([^,)]+)(?:,[^)]*)?\)/, `rgba($1,$2,$3, ${alpha})`);

const BAND_SERIES = "band";

// Bands narrower than this share of the range leave out their label, so frequent
// switches don't stack labels; the timelines' tooltips still name them.
const BAND_LABEL_MIN_SHARE = 0.05;

/** Plot margins above and below, for the unit name and the time labels. */
export const PLOT_TOP = 28;
export const PLOT_BOTTOM = 28;

export const formatValue = (value: number, unit: string | null) =>
  `${value.toLocaleString(undefined, { maximumFractionDigits: 2 })}${unit ? ` ${unit}` : ""}`;

const escapeHtml = (text: string) =>
  text.replace(
    /[&<>"]/g,
    (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[char]!,
  );

/** Show only `name`, or add it to or take it from those shown; null shows all. */
export function toggleShown(
  shown: ReadonlySet<string> | null,
  name: string,
  all: string[],
): Set<string> | null {
  if (shown === null) return new Set([name]);
  const next = new Set(shown);
  if (!next.delete(name)) next.add(name);
  return next.size === 0 || all.every((entry) => next.has(entry)) ? null : next;
}

/** Show only the names of a group; clicking the group shown alone shows all again. */
export function showGroup(shown: ReadonlySet<string> | null, names: string[]): Set<string> | null {
  const same =
    shown !== null && shown.size === names.length && names.every((name) => shown.has(name));
  return same || !names.length ? null : new Set(names);
}

function bandSeries(layer: BandLayer, index: number, input: TrendOptionInput): SeriesOption {
  const { colors, range } = input;
  return {
    type: "line",
    id: `${BAND_SERIES}-${index}`,
    data: [],
    silent: true,
    markArea: {
      silent: true,
      data: layer.bands.map((band) => {
        const color = colors.bands[band.mode] ?? colors.grid;
        return [
          {
            name: band.label,
            xAxis: Math.max(band.start, range.start),
            itemStyle: {
              color: withAlpha(color, 0.07),
              borderColor: withAlpha(color, 0.25),
              borderType: "dashed",
              borderWidth: 1,
            },
            label: {
              show: (band.end - band.start) / (range.end - range.start) >= BAND_LABEL_MIN_SHARE,
              color: colors.text,
              fontSize: 10,
              position: layer.labelAt === "top" ? "insideTop" : "insideBottom",
            },
          },
          { xAxis: Math.min(band.end, range.end) },
        ];
      }),
    },
  };
}

function limitSeries({ limits, range, colors }: TrendOptionInput): SeriesOption[] {
  const lines: SeriesOption[] = [limits.lower, limits.upper].flatMap((limit) =>
    limit
      ? [
          {
            type: "line",
            id: `${BAND_SERIES}-limit-${limit.name}`,
            name: limit.name,
            data: heldUntil(limit, range.end),
            step: "end",
            showSymbol: false,
            color: colors.limit,
            lineStyle: { width: 1, type: "dashed" },
            emphasis: { disabled: true },
          } satisfies SeriesOption,
        ]
      : [],
  );
  if (!limits.lower || !limits.upper) return lines;
  // Rectangles in data space, so the band follows the value axis however it scales.
  const area: SeriesOption = {
    type: "line",
    id: `${BAND_SERIES}-limits`,
    data: [],
    silent: true,
    markArea: {
      silent: true,
      itemStyle: { color: withAlpha(colors.limit, 0.16) },
      data: limitRects(limits.lower, limits.upper, range).map(({ start, end, low, high }) => [
        { xAxis: start, yAxis: low },
        { xAxis: end, yAxis: high },
      ]),
    },
  };
  return [area, ...lines];
}

export function trendOption(input: TrendOptionInput): EChartsOption {
  const {
    lines,
    hidden,
    layers,
    range,
    unit,
    colors,
    mode,
    kind = "line",
    binWidth,
    totalLabel = "Total",
  } = input;
  const names = lines.map((line) => line.name);

  const dataSeries: SeriesOption[] = lines
    .filter((line) => !hidden.has(line.name))
    .map((line): SeriesOption => {
      const { color, dashed } = seriesColor(line.name, names, mode);
      return {
        type: "line",
        name: line.name,
        data: line.points,
        showSymbol: false,
        // Sampled per line, stacked areas would no longer share their times.
        sampling: kind === "stacked" ? undefined : "lttb",
        connectNulls: false,
        color,
        // Stacked, a source at zero would draw its line along the top of the others.
        lineStyle: { width: kind === "stacked" ? 0 : 2, type: dashed ? "dashed" : "solid" },
        emphasis: { disabled: true },
        ...(kind === "stacked" ? { stack: "total", areaStyle: { opacity: 0.85 } } : {}),
        ...(kind === "area" ? { areaStyle: { opacity: 0.2 } } : {}),
      };
    });

  return {
    animation: false,
    backgroundColor: "transparent",
    grid: {
      left: PLOT_INSET.left,
      right: PLOT_INSET.right,
      top: PLOT_TOP,
      bottom: PLOT_BOTTOM,
      containLabel: false,
    },
    tooltip: {
      trigger: "axis",
      // On top of the page, so the edge of the tile doesn't cut it off.
      appendTo: "body",
      backgroundColor: "transparent",
      borderWidth: 0,
      padding: 0,
      extraCssText: "box-shadow: none;",
      axisPointer: { type: "line", lineStyle: { color: colors.text, opacity: 0.5 } },
      formatter: (params) => {
        const items = (Array.isArray(params) ? params : [params]).filter(
          (item) => !String(item.seriesId ?? "").startsWith(BAND_SERIES) && item.seriesName,
        );
        const first = items[0] as { axisValue?: number } | undefined;
        if (first?.axisValue === undefined) return "";
        // A point averaging a period sits in its middle.
        const from = binWidth ? first.axisValue - binWidth / 2 : first.axisValue;
        const timeLabel = binWidth
          ? `${new Date(from).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" })} – ${new Date(
              from + binWidth,
            ).toLocaleTimeString(undefined, { timeStyle: "short" })}`
          : new Date(from).toLocaleString(undefined, {
              dateStyle: "medium",
              timeStyle: "medium",
            });
        const rows = items.flatMap((item) => {
          const value = (item.value as [number, number | null])[1];
          if (value === null || value === undefined) return [];
          return [
            `<div class="flex items-center gap-2"><span class="size-2 shrink-0 rounded-full" style="background:${String(item.color)}"></span><span class="grow">${escapeHtml(item.seriesName ?? "")}</span><span class="pl-4 font-semibold tabular-nums">${formatValue(value, unit)}</span></div>`,
          ];
        });
        // Stacked areas add up, so show their sum too.
        const sum = items.reduce(
          (total, item) => total + ((item.value as [number, number | null])[1] ?? 0),
          0,
        );
        const total =
          kind === "stacked" && rows.length > 1
            ? `<div class="mt-1 flex justify-between border-t border-current/20 pt-1 font-semibold"><span>${escapeHtml(totalLabel)}</span><span class="tabular-nums">${formatValue(sum, unit)}</span></div>`
            : "";
        return `<div class="${TOOLTIP_CLASS} min-w-48"><div class="mb-1 opacity-70">${timeLabel}</div>${rows.join("")}${total}</div>`;
      },
    },
    xAxis: {
      type: "time",
      min: range.start,
      max: range.end,
      axisLabel: { color: colors.text, fontSize: 10, hideOverlap: true },
      axisLine: { lineStyle: { color: colors.grid } },
      splitLine: { show: false },
    },
    yAxis: {
      type: "value",
      scale: kind === "line",
      // Headroom, so a limit at the top or bottom stays visible.
      ...(kind === "line" ? { boundaryGap: ["6%", "6%"] as [string, string] } : {}),
      name: unit ?? undefined,
      nameGap: 12,
      nameTextStyle: { color: colors.text, fontSize: 10, align: "right" },
      axisLabel: {
        color: colors.text,
        fontSize: 10,
        width: PLOT_INSET.left - 12,
        overflow: "truncate",
      },
      splitLine: { lineStyle: { color: colors.grid, opacity: 0.5 } },
    },
    series: [
      ...layers.map((layer, index) => bandSeries(layer, index, input)),
      ...limitSeries(input),
      ...dataSeries,
    ],
  };
}
