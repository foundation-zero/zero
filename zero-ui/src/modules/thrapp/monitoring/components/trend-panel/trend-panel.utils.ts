import { MonitoringMetric, TICK_STEPS } from "@/modules/thrapp/monitoring/monitoring.consts";
import type {
  DeviceSeries,
  LatestValueRow,
  LegendGroup,
  MetricSeries,
  ResolvedRange,
  TotalRow,
  TrendLimit,
  TrendLine,
  TrendPanelConfig,
} from "@/modules/thrapp/monitoring/monitoring.types";
import { withGaps } from "@/modules/thrapp/monitoring/monitoring.utils";

const ACRONYMS: Record<string, string> = { dc: "DC", hvac: "HVAC", ht: "HT", hp: "HP", lt: "LT" };

// The kind of device, which the panel's title already says.
const DEVICE_KINDS = /^(temperature|flow|switch|level|pressure|flowcontrol)-(?=.)/;

/**
 * A device name for the narrow table: without the module prefix and kind the
 * panel already says, in words, e.g. dhw-temperature-hvac-exchanger-return
 * becomes "Hvac exchanger return".
 */
export const shortDeviceName = (device: string) => {
  const name = device
    .replace(/^[a-z]+-(?=.)/, "")
    .replace(DEVICE_KINDS, "")
    .split("-")
    .map((word) => ACRONYMS[word] ?? word)
    .join(" ");
  return name.charAt(0).toUpperCase() + name.slice(1);
};

export const deviceLabel = (device: DeviceSeries, config: TrendPanelConfig) =>
  config.deviceLabels?.[device.device] ??
  (device.yardTag ? `[${device.yardTag}] ${device.device}` : device.device);

const metricOf = (series: MetricSeries[], metric: MonitoringMetric | undefined) =>
  series.find((entry) => entry.metric === metric);

/** The devices of a metric, in the order the panel lists them, so stacks and colours hold. */
const devicesOf = (series: MetricSeries[], metric: MonitoringMetric, config: TrendPanelConfig) => {
  const devices = metricOf(series, metric)?.devices ?? [];
  const order = config.devices;
  if (!order) return devices;
  const rank = (device: DeviceSeries) => {
    const index = order.indexOf(device.device);
    return index === -1 ? order.length : index;
  };
  return devices.toSorted((a, b) => rank(a) - rank(b));
};

export const trendLines = (
  series: MetricSeries[],
  metric: MonitoringMetric,
  config: TrendPanelConfig,
): TrendLine[] =>
  devicesOf(series, metric, config).map((device) => ({
    name: deviceLabel(device, config),
    device: device.device,
    points: withGaps(device.times.map(Date.parse), device.values),
  }));

export function trendLimit(
  series: MetricSeries[],
  metric: MonitoringMetric | undefined,
  name: string,
): TrendLimit | undefined {
  const [device] = metricOf(series, metric)?.devices ?? [];
  if (!device?.times.length) return undefined;
  return {
    name,
    points: device.times.map((time, index): [number, number] => [
      Date.parse(time),
      device.values[index],
    ]),
  };
}

export const latestRows = (
  series: MetricSeries[],
  metric: MonitoringMetric,
  config: TrendPanelConfig,
): LatestValueRow[] =>
  devicesOf(series, metric, config).map((device) => ({
    asset: deviceLabel(device, config),
    shortName: config.deviceLabels?.[device.device] ?? shortDeviceName(device.device),
    value: device.latest?.value ?? null,
    timestamp: device.latest ? Date.parse(device.latest.timestamp) : null,
  }));

/** The configured legend groups, with the names of the lines they hold. */
export const legendGroups = (
  lines: TrendLine[],
  config: TrendPanelConfig,
  label: (key: string) => string,
): LegendGroup[] =>
  (config.legendGroups ?? []).map(({ key, devices }) => ({
    key,
    label: label(key),
    names: devices.flatMap((device) => lines.find((line) => line.device === device)?.name ?? []),
  }));

/** The metrics of a panel by their label, for the drop-down. */
export const sortedMetrics = (
  metrics: MonitoringMetric[],
  label: (metric: MonitoringMetric) => string,
) => metrics.toSorted((a, b) => label(a).localeCompare(label(b)));

/**
 * Lines ready to stack: every line on the same times, with a gap or power below
 * zero (noise while a circuit stands still) as zero. Lines on different times,
 * or with gaps, make the stacked areas cut wedges into each other.
 */
export function stackable(lines: TrendLine[]): TrendLine[] {
  const times = [...new Set(lines.flatMap((line) => line.points.map(([time]) => time)))].sort(
    (a, b) => a - b,
  );
  return lines.map((line) => {
    const values = new Map(line.points.map(([time, value]) => [time, value]));
    return {
      ...line,
      points: times.map((time): [number, number] => [time, Math.max(values.get(time) ?? 0, 0)]),
    };
  });
}

/** Energy per device in kWh from binned power in kW, the largest first. */
export function energyRows(
  series: MetricSeries[],
  metric: MonitoringMetric,
  config: TrendPanelConfig,
): TotalRow[] {
  const entry = metricOf(series, metric);
  const hours = (entry?.binSeconds ?? 0) / 3600;
  return devicesOf(series, metric, config)
    .map((device) => ({
      asset: deviceLabel(device, config),
      shortName: config.deviceLabels?.[device.device],
      value: device.values.reduce((sum, value) => sum + Math.max(value, 0) * hours, 0),
    }))
    .toSorted((a, b) => b.value - a.value);
}

/** About this many periods across the range for the water flows. */
const WATER_PERIODS = 96;

export const waterPeriod = ({ start, end }: ResolvedRange) =>
  TICK_STEPS.find((step) => (end - start) / step <= WATER_PERIODS) ??
  TICK_STEPS[TICK_STEPS.length - 1];

export type WaterFlows = {
  /** Fresh water into the tanks, in L/min per period. */
  inflow: [number, number | null][];
  /** Hot water drawn from the tanks, in L/min per period. */
  outflow: [number, number | null][];
  period: number;
};

/**
 * Fresh water in, averaged per period, and hot water out, which no meter
 * measures: what came in less what the tanks gained, as the tanks only take in
 * fresh water and only give out hot water.
 */
export function waterFlows(
  series: MetricSeries[],
  freshwater: string,
  tanks: string[],
  range: ResolvedRange,
): WaterFlows {
  const period = waterPeriod(range);
  const count = Math.ceil((range.end - range.start) / period);
  const periodOf = (time: number) => Math.floor((time - range.start) / period);

  const inflowSum = Array.from({ length: count }, () => 0);
  const inflowCount = Array.from({ length: count }, () => 0);
  const flow = metricOf(series, MonitoringMetric.CalculatedFlow)?.devices.find(
    (device) => device.device === freshwater,
  );
  flow?.times.forEach((time, index) => {
    const at = periodOf(Date.parse(time));
    if (at < 0 || at >= count) return;
    inflowSum[at] += flow.values[index];
    inflowCount[at]++;
  });

  // The volume in all tanks, at the bins where every tank reported.
  const volumes = new Map<number, { sum: number; tanks: number }>();
  for (const device of metricOf(series, MonitoringMetric.Level)?.devices ?? []) {
    if (!tanks.includes(device.device)) continue;
    device.times.forEach((time, index) => {
      const at = Date.parse(time);
      const volume = volumes.get(at) ?? { sum: 0, tanks: 0 };
      volumes.set(at, { sum: volume.sum + device.values[index], tanks: volume.tanks + 1 });
    });
  }
  // The last full reading of each period.
  const lastVolume: ({ time: number; volume: number } | undefined)[] = Array.from({
    length: count,
  });
  [...volumes.entries()]
    .filter(([, volume]) => volume.tanks === tanks.length)
    .toSorted(([a], [b]) => a - b)
    .forEach(([time, volume]) => {
      const at = periodOf(time);
      if (at >= 0 && at < count) lastVolume[at] = { time, volume: volume.sum };
    });

  const inflow: [number, number | null][] = [];
  const outflow: [number, number | null][] = [];
  let previous: { time: number; volume: number } | undefined;
  for (let at = 0; at < count; at++) {
    const middle = range.start + (at + 0.5) * period;
    const coming = inflowCount[at] ? inflowSum[at] / inflowCount[at] : null;
    const current = lastVolume[at];
    const gained =
      current && previous
        ? (current.volume - previous.volume) / ((current.time - previous.time) / 60_000)
        : null;
    inflow.push([middle, coming]);
    outflow.push([
      middle,
      coming === null || gained === null ? null : Math.max(coming - gained, 0),
    ]);
    if (current) previous = current;
  }
  return { inflow, outflow, period };
}

/** Litres over the range from flows in L/min per period. */
export const litres = (points: [number, number | null][], period: number) =>
  points.reduce((sum, [, value]) => sum + (value ?? 0) * (period / 60_000), 0);
