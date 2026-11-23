import type { ModeBadgeMode } from "@/modules/thrapp/mimics/components/mode-badge/mode-badge.consts";
import type { MonitoringMetric, MonitoringSignal } from "./monitoring.consts";

/** A window of `span` ms that ends at `end`, or at now while `end` is null. */
export type TimeRange = {
  span: number;
  end: number | null;
};

export type ResolvedRange = {
  start: number;
  end: number;
};

export type Reading = {
  value: number;
  timestamp: string;
};

export type DeviceSeries = {
  device: string;
  yardTag: string | null;
  times: string[];
  values: number[];
  latest: Reading | null;
};

export type MetricSeries = {
  metric: MonitoringMetric;
  unit: string | null;
  step: boolean;
  binSeconds: number | null;
  devices: DeviceSeries[];
};

export type Segment = {
  state: string;
  start: string;
  end: string;
};

export type SignalStates = {
  signal: MonitoringSignal;
  segments: Segment[];
};

/** How a state looks: the mimics' badge colour and a readable label. */
export type StateStyle = {
  mode: ModeBadgeMode;
  label: string;
};

export type StateTotal = StateStyle & {
  state: string;
  seconds: number;
};

export type StyledSegment = StateStyle & {
  state: string;
  start: number;
  end: number;
};

export type TimelineRow = {
  label: string;
  segments: StyledSegment[];
};

export type TrendLine = {
  name: string;
  /** The device the line belongs to, for legend groups. */
  device?: string;
  points: [number, number | null][];
};

export type TrendBand = {
  label: string;
  mode: ModeBadgeMode;
  start: number;
  end: number;
};

/** Bands of one signal behind a chart, with the switch that shows them. */
export type ChartOverlay = {
  key: string;
  label: string;
  bands: TrendBand[];
  /** Whether the bands show until the viewer switches them. */
  shown: boolean;
};

export type TrendLimit = {
  name: string;
  points: [number, number][];
};

export type LatestValueRow = {
  /** The name in the chart's legend. */
  asset: string;
  /** A shorter name for the narrow table, without the yard tag. */
  shortName?: string;
  value: number | null;
  timestamp: number | null;
  /** The line colour of the asset in the chart beside the table. */
  color?: string;
  dashed?: boolean;
};

export type StateRowConfig = {
  signal: MonitoringSignal;
  /** Key under thrapp.monitoring.rows, with its parameters. */
  label: { key: string; params?: Record<string, unknown> };
};

/** A timeline of one or more signals with their distribution beside it. */
export type StatePanelConfig = {
  /** Title under thrapp.monitoring.sections, and the key that remembers it open. */
  key: string;
  header: "mode" | "tankState";
  rows: StateRowConfig[];
};

/** A trend chart with the latest values beside it. */
export type TrendPanelConfig = {
  /** Title under thrapp.monitoring.sections, and the key that remembers it open. */
  key: string;
  /** With more than one, a drop-down picks one, listed alphabetically. */
  metrics: MonitoringMetric[];
  /** Shown first; defaults to the first of `metrics`. */
  defaultMetric?: MonitoringMetric;
  devices?: string[];
  /** Shorter names for devices, e.g. "Tank 1"; others show as "[yard tag] device". */
  deviceLabels?: Record<string, string>;
  /** Signals whose states can be drawn as bands behind the lines, each with its own switch. */
  overlays?: OverlayConfig[];
  /** Legend groups; a click on a group shows only its devices. */
  legendGroups?: LegendGroupConfig[];
  limits?: { lower: MonitoringMetric; upper: MonitoringMetric };
  /** Adds a totals row to the table. */
  totals?: boolean;
  /**
   * `line` draws each device and its latest value; `heat` stacks power per
   * source with the energy each delivered; `distribution` shows that energy as
   * a treemap and a pie; `water` shows fresh water in and hot water out.
   */
  display?: "line" | "heat" | "distribution" | "water";
};

/** A device's share of a total over the range, e.g. energy or volume. */
export type TotalRow = {
  asset: string;
  /** Leaves the row out of the shares and the sum, e.g. a net change. */
  derived?: boolean;
  shortName?: string;
  value: number;
  color?: string;
  dashed?: boolean;
};

export type OverlayConfig = {
  signal: MonitoringSignal;
  /** Whether the bands show until the viewer switches them. */
  shown: boolean;
};

export type LegendGroupConfig = {
  /** Name under thrapp.monitoring.groups. */
  key: string;
  devices: string[];
};

/** A legend group with the line names it holds. */
export type LegendGroup = {
  key: string;
  label: string;
  names: string[];
};

export type ModuleMonitoring = {
  /** The module as the API names it. */
  module: string;
  states: { section: string; panels: StatePanelConfig[] }[];
  trends: { section: string; panels: TrendPanelConfig[] }[];
};

export type AnnotationKind = "CREW" | "PARAMETERS" | "ALARM";

export type ParameterChange = {
  name: string;
  previous: string | null;
  value: string | null;
};

/** A note at a moment: the crew's own, a parameter change or a module alarm. */
export type MonitoringAnnotation = {
  id: string;
  kind: AnnotationKind;
  time: string;
  /** The crew's note; the changed parameters; or raised / cleared for alarms. */
  text: string;
  author: string | null;
  /** Written from this browser, so it may delete it. */
  canDelete: boolean;
  changes: ParameterChange[];
};
