import { tScoped } from "@/modules/common/lib/utils";
import { ModeBadgeMode } from "@/modules/thrapp/mimics/components/mode-badge/mode-badge.consts";
import { useEventListener, useLocalStorage, useMutationObserver } from "@vueuse/core";
import { format } from "date-fns";
import { computed, type MaybeRefOrGetter, ref, type Ref, toValue } from "vue";
import {
  DEFAULT_SPAN,
  GAP_AFTER,
  MAX_SPAN,
  MonitoringSignal,
  RANGE_PRESETS,
  SERIES_COLORS,
  SIGNAL_MODES,
  TICK_STEPS,
} from "./monitoring.consts";
import type {
  DeviceSeries,
  MonitoringAnnotation,
  ResolvedRange,
  Segment,
  StateStyle,
  TimeRange,
  TrendLimit,
} from "./monitoring.types";

const DAY = 86_400_000;

export function resolveRange({ span, end }: TimeRange, now: number): ResolvedRange {
  const resolvedEnd = end ?? now;
  return { start: resolvedEnd - span, end: resolvedEnd };
}

export const isLive = (range: TimeRange) => range.end === null;

/** Move the window by one span; reaching now makes it live again. */
export function shiftRange(range: TimeRange, direction: -1 | 1, now: number): TimeRange {
  const end = (range.end ?? now) + direction * range.span;
  return { span: range.span, end: end >= now ? null : end };
}

/** Double the span around the same end, up to the longest allowed range. */
export const zoomOut = (range: TimeRange): TimeRange => ({
  ...range,
  span: Math.min(range.span * 2, MAX_SPAN),
});

/** Shortest range a drag can zoom to. */
const MIN_SPAN = 60_000;

/** A dragged stretch of time as a fixed range, at least a minute long. */
export function zoomedRange({ start, end }: ResolvedRange, now: number): TimeRange {
  // Whole minutes, as the URL keeps the span.
  const span = Math.max(Math.round((end - start) / MIN_SPAN) * MIN_SPAN, MIN_SPAN);
  const fixedEnd = Math.round(Math.max(end, start + span));
  return { span, end: Math.min(fixedEnd, now) };
}

export type CustomRangeResult = { range: TimeRange } | { error: "invalid" | "order" | "tooLong" };

/**
 * A range typed as start and end times; an end at or past now follows now.
 * Errors name a key under thrapp.monitoring.timeRange.errors.
 */
export function customRange(start: number, end: number, now: number): CustomRangeResult {
  if (!Number.isFinite(start) || !Number.isFinite(end)) return { error: "invalid" };
  const clippedEnd = Math.min(end, now);
  if (clippedEnd - start < MIN_SPAN) return { error: "order" };
  if (clippedEnd - start > MAX_SPAN) return { error: "tooLong" };
  const span = Math.round((clippedEnd - start) / MIN_SPAN) * MIN_SPAN;
  return { range: { span, end: end >= now ? null : clippedEnd } };
}

export function presetKey(span: number): string | undefined {
  return RANGE_PRESETS.find((preset) => preset.span === span)?.key;
}

function spanFromKey(key: string): number | undefined {
  const match = /^(\d+)([mhd])$/.exec(key);
  if (!match) return undefined;
  const [, amount, unit] = match;
  const unitMs = { m: 60_000, h: 3_600_000, d: DAY }[unit as "m" | "h" | "d"];
  return Number(amount) * unitMs;
}

function spanKey(span: number): string {
  if (span % DAY === 0) return `${span / DAY}d`;
  if (span % 3_600_000 === 0) return `${span / 3_600_000}h`;
  return `${Math.round(span / 60_000)}m`;
}

/** Read a range from the URL query, falling back to the default for anything invalid. */
export function rangeFromQuery(query: Record<string, unknown>): TimeRange {
  const span = typeof query.range === "string" ? spanFromKey(query.range) : undefined;
  const end = typeof query.end === "string" ? Date.parse(query.end) : NaN;
  return {
    span: span && span > 0 ? Math.min(span, MAX_SPAN) : DEFAULT_SPAN,
    end: Number.isFinite(end) ? end : null,
  };
}

export function rangeToQuery(range: TimeRange): Record<string, string | undefined> {
  return {
    range: spanKey(range.span),
    end: range.end === null ? undefined : new Date(range.end).toISOString(),
  };
}

export type DurationParts = { days: number; hours: number; minutes: number; seconds: number };

export function durationParts(totalSeconds: number): DurationParts {
  const rounded = Math.max(0, Math.round(totalSeconds));
  return {
    days: Math.floor(rounded / 86_400),
    hours: Math.floor((rounded % 86_400) / 3_600),
    minutes: Math.floor((rounded % 3_600) / 60),
    seconds: rounded % 60,
  };
}

/** Evenly spaced round times inside the range, for an axis of about `count` ticks. */
export function timeTicks({ start, end }: ResolvedRange, count = 8): number[] {
  const step =
    TICK_STEPS.find((size) => (end - start) / size <= count) ?? TICK_STEPS[TICK_STEPS.length - 1];
  // Align to local midnight so day and hour ticks fall on round local times.
  const offset = new Date(start).getTimezoneOffset() * 60_000;
  const first = Math.ceil((start - offset) / step) * step + offset;
  return Array.from(
    { length: Math.floor((end - first) / step) + 1 },
    (_, index) => first + index * step,
  );
}

export function tickLabel(tick: number, { start, end }: ResolvedRange): string {
  return end - start > 2 * DAY ? format(tick, "dd MMM") : format(tick, "HH:mm");
}

/** Pair times with values and break the line where samples are missing. */
export function withGaps(
  times: number[],
  values: number[],
  gapAfter: number = GAP_AFTER,
): [number, number | null][] {
  return times.flatMap((time, index): [number, number | null][] => {
    const previous = times[index - 1];
    const point: [number, number] = [time, values[index]];
    return previous !== undefined && time - previous > gapAfter
      ? [[previous + 1, null], point]
      : [point];
  });
}

/** Colour per device by its place among the sorted names, so the response order doesn't matter. */
export function seriesColor(
  name: string,
  names: string[],
  mode: "light" | "dark",
): { color: string; dashed: boolean } {
  const palette = SERIES_COLORS[mode];
  const index = names.toSorted().indexOf(name);
  return { color: palette[index % palette.length], dashed: index >= palette.length };
}

/**
 * Replace the overlapping tail of `previous` with `update` and drop what fell
 * out of the window, so a refresh only has to fetch the newest part.
 */
export function mergeDeviceSeries(
  previous: DeviceSeries[],
  update: DeviceSeries[],
  windowStart: number,
): DeviceSeries[] {
  const devices = new Set([...previous, ...update].map((series) => series.device));
  return [...devices].toSorted().map((device) => {
    const old = previous.find((series) => series.device === device);
    const fresh = update.find((series) => series.device === device);
    const cut = fresh?.times[0] ? Date.parse(fresh.times[0]) : Infinity;
    const kept = (old?.times ?? []).flatMap((time, index) => {
      const at = Date.parse(time);
      return at >= windowStart && at < cut ? [[time, old!.values[index]] as const] : [];
    });
    return {
      device,
      yardTag: fresh?.yardTag ?? old?.yardTag ?? null,
      times: [...kept.map(([time]) => time), ...(fresh?.times ?? [])],
      values: [...kept.map(([, value]) => value), ...(fresh?.values ?? [])],
      latest: fresh?.latest ?? old?.latest ?? null,
    };
  });
}

/** As mergeDeviceSeries, for state segments; touching segments of one state join up. */
export function mergeSegments(
  previous: Segment[],
  update: Segment[],
  windowStart: number,
): Segment[] {
  const cut = update[0] ? Date.parse(update[0].start) : Infinity;
  const kept = previous.flatMap((segment) => {
    const start = Math.max(Date.parse(segment.start), windowStart);
    const end = Math.min(Date.parse(segment.end), cut);
    return end > start
      ? [
          {
            state: segment.state,
            start: new Date(start).toISOString(),
            end: new Date(end).toISOString(),
          },
        ]
      : [];
  });
  return [...kept, ...update].reduce<Segment[]>((joined, segment) => {
    const last = joined[joined.length - 1];
    if (last && last.state === segment.state && Date.parse(last.end) >= Date.parse(segment.start)) {
      return [...joined.slice(0, -1), { ...last, end: segment.end }];
    }
    return [...joined, segment];
  }, []);
}

export function stateTotals(segments: Segment[]): Map<string, number> {
  return segments.reduce(
    (totals, { state, start, end }) =>
      totals.set(state, (totals.get(state) ?? 0) + (Date.parse(end) - Date.parse(start)) / 1000),
    new Map<string, number>(),
  );
}

/** Points that hold until the next one, as `step: true` series come back from the API. */
export const stepValueAt = (limit: TrendLimit, time: number): number | undefined =>
  limit.points.findLast(([at]) => at <= time)?.[1];

export type LimitRect = { start: number; end: number; low: number; high: number };

/**
 * The area between a lower and upper limit as one rectangle per period in which
 * neither changed, clipped to the range and held until its end.
 */
export function limitRects(
  lower: TrendLimit,
  upper: TrendLimit,
  { start, end }: ResolvedRange,
): LimitRect[] {
  const changes = [...lower.points, ...upper.points]
    .map(([time]) => Math.max(time, start))
    .filter((time) => time < end);
  const times = [...new Set(changes)].toSorted((a, b) => a - b);
  return times.flatMap((time, index) => {
    const low = stepValueAt(lower, time);
    const high = stepValueAt(upper, time);
    if (low === undefined || high === undefined) return [];
    return [{ start: time, end: times[index + 1] ?? end, low, high }];
  });
}

/** A stepped limit held until the end of the range, so its line reaches the edge. */
export function heldUntil(limit: TrendLimit, end: number): [number, number][] {
  const last = limit.points[limit.points.length - 1];
  return last && last[0] < end ? [...limit.points, [end, last[1]]] : limit.points;
}

/**
 * The colour a CSS value such as `var(--heating-medium)` resolves to, as rgb().
 * ECharts can't read custom properties or oklch, so paint it once and read it back.
 */
export function resolveCssColor(
  value: string,
  element: Element = document.documentElement,
): string {
  const probe = document.createElement("span");
  probe.style.color = value;
  probe.style.display = "none";
  element.appendChild(probe);
  const computed = getComputedStyle(probe).color;
  probe.remove();

  const context = document.createElement("canvas").getContext("2d");
  if (!context) return computed || value;
  context.fillStyle = computed || value;
  context.fillRect(0, 0, 1, 1);
  const [red, green, blue, alpha] = context.getImageData(0, 0, 1, 1).data;
  return `rgba(${red}, ${green}, ${blue}, ${(alpha / 255).toFixed(3)})`;
}

/** Label and badge colour of a state, as the mimics show it. */
export function useStateStyles() {
  const t = tScoped("thrapp.monitoring.states");

  return (signal: MonitoringSignal, state: string): StateStyle => {
    const group = signal.startsWith("TANK_") ? "TANK" : signal;
    const key = `${group}.${state.replace(/ /g, "_")}`;
    return {
      mode: SIGNAL_MODES[signal][state] ?? ModeBadgeMode.Idle,
      label: t.exists(key) ? t(key) : state,
    };
  };
}

/** "12hr 30 min 10 sec", leaving out leading zero parts. */
export function useDurationFormat() {
  const t = tScoped("thrapp.monitoring.duration");

  /** From the largest unit down; `units` keeps only that many, e.g. "6d 12hr". */
  return (seconds: number, units = 4) => {
    const parts = durationParts(seconds);
    const names = ["days", "hours", "minutes", "seconds"] as const;
    const first = names.findIndex((unit) => parts[unit] > 0);
    const from = first === -1 ? names.length - 1 : first;
    return names
      .slice(from, from + units)
      .map((unit) => t(unit, { count: parts[unit] }))
      .join(" ");
  };
}

/** Light or dark around `element`, following the `dark` class the app sets on <html>. */
export function useThemeMode(element: Readonly<Ref<HTMLElement | null>>) {
  const themeChanges = ref(0);
  // Watching only <html> keeps charts, which change their own classes while drawing, out of it.
  useMutationObserver(document.documentElement, () => themeChanges.value++, {
    attributes: true,
    attributeFilter: ["class"],
  });

  const mode = computed<"light" | "dark">(() => {
    void themeChanges.value;
    return element.value?.closest(".dark") ? "dark" : "light";
  });
  return { mode, themeChanges };
}

/**
 * Theme colours resolved for ECharts inside `element`, so a chart under a
 * `.dark` wrapper gets the dark values; they resolve again when the theme changes.
 */
export function useCssColors<Key extends string>(
  values: MaybeRefOrGetter<Record<Key, string>>,
  element: Readonly<Ref<HTMLElement | null>>,
) {
  const { mode, themeChanges } = useThemeMode(element);
  const colors = computed(() => {
    void themeChanges.value;
    const target = element.value ?? document.documentElement;
    return Object.fromEntries(
      Object.entries<string>(toValue(values)).map(([key, value]) => [
        key,
        resolveCssColor(value, target),
      ]),
    ) as Record<Key, string>;
  });
  return { colors, mode };
}

/** Pointer drags shorter than this are clicks, not a zoom. */
const MIN_DRAG = 6;

/**
 * Drag across the plot of a timeline or chart to zoom to that stretch of time.
 * Listens on the container, so the chart under it keeps its own hover.
 */
export function usePlotDrag(
  element: Readonly<Ref<HTMLElement | null>>,
  range: MaybeRefOrGetter<ResolvedRange>,
  inset: { left: number; right: number },
  onZoom: (range: ResolvedRange) => void,
) {
  const from = ref<number | null>(null);
  const to = ref<number | null>(null);

  const plot = () => {
    const box = element.value?.getBoundingClientRect();
    return box
      ? { left: box.left + inset.left, width: box.width - inset.left - inset.right }
      : null;
  };
  const offset = (event: PointerEvent) => {
    const area = plot();
    return area ? Math.min(Math.max(event.clientX - area.left, 0), area.width) : null;
  };

  const onDown = (event: PointerEvent) => {
    const area = plot();
    if (event.button !== 0 || !area) return;
    const x = event.clientX - area.left;
    if (x < 0 || x > area.width) return;
    from.value = x;
    to.value = x;
  };
  const onMove = (event: PointerEvent) => {
    if (from.value !== null) to.value = offset(event);
  };
  const onUp = () => {
    const area = plot();
    if (
      from.value !== null &&
      to.value !== null &&
      area &&
      Math.abs(to.value - from.value) >= MIN_DRAG
    ) {
      const { start, end } = toValue(range);
      const at = (x: number) => start + (x / area.width) * (end - start);
      onZoom({
        start: at(Math.min(from.value, to.value)),
        end: at(Math.max(from.value, to.value)),
      });
    }
    from.value = null;
    to.value = null;
  };

  useEventListener(element, "pointerdown", onDown);
  useEventListener(window, "pointermove", onMove);
  useEventListener(window, "pointerup", onUp);

  /** The dragged stretch in px from the container's left edge, while dragging. */
  const selection = computed(() =>
    from.value === null || to.value === null || Math.abs(to.value - from.value) < MIN_DRAG
      ? null
      : {
          left: inset.left + Math.min(from.value, to.value),
          width: Math.abs(to.value - from.value),
        },
  );
  return { selection, dragging: computed(() => from.value !== null) };
}

/**
 * Who writes annotations from this browser: a name the crew member types, and
 * a key that lets this browser delete what it wrote. THRS has no login.
 */
export function useAnnotationIdentity() {
  const ownerKey = useLocalStorage("thrs-monitoring-annotation-owner", () => crypto.randomUUID());
  const author = useLocalStorage("thrs-monitoring-annotation-author", "");
  return { ownerKey, author };
}

/** Annotations of the shown kinds that fall in the range, with their place on it in %. */
export const placeAnnotations = (
  annotations: MonitoringAnnotation[],
  shown: ReadonlySet<string>,
  { start, end }: ResolvedRange,
) =>
  annotations.flatMap((annotation) => {
    const time = Date.parse(annotation.time);
    return shown.has(annotation.kind) && time >= start && time <= end
      ? [{ annotation, left: ((time - start) / (end - start)) * 100 }]
      : [];
  });
