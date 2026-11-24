import type { MonitoringSignal } from "@/modules/thrapp/monitoring/monitoring.consts";
import type {
  ResolvedRange,
  SignalStates,
  StatePanelConfig,
  StateRowConfig,
  StateStyle,
  StateTotal,
  StyledSegment,
  TimelineRow,
} from "@/modules/thrapp/monitoring/monitoring.types";

type StyleOf = (signal: MonitoringSignal, state: string) => StateStyle;

export function styledSegments(
  signal: MonitoringSignal,
  states: SignalStates[],
  styleOf: StyleOf,
): StyledSegment[] {
  const segments = states.find((entry) => entry.signal === signal)?.segments ?? [];
  return segments.map(({ state, start, end }) => ({
    state,
    ...styleOf(signal, state),
    start: Date.parse(start),
    end: Date.parse(end),
  }));
}

export const panelRows = (
  config: StatePanelConfig,
  states: SignalStates[],
  styleOf: StyleOf,
  labelOf: (label: StateRowConfig["label"]) => string,
): TimelineRow[] =>
  config.rows.map((row) => ({
    label: labelOf(row.label),
    segments: styledSegments(row.signal, states, styleOf),
  }));

/** Time per state over all of the panel's signals, clipped to the range, longest first. */
export function panelTotals(
  config: StatePanelConfig,
  states: SignalStates[],
  range: ResolvedRange,
  styleOf: StyleOf,
): StateTotal[] {
  const totals = new Map<string, StateTotal>();
  config.rows.forEach(({ signal }) => {
    styledSegments(signal, states, styleOf).forEach((segment) => {
      const seconds =
        (Math.min(segment.end, range.end) - Math.max(segment.start, range.start)) / 1000;
      if (seconds <= 0) return;
      const total = totals.get(segment.state);
      totals.set(segment.state, {
        state: segment.state,
        mode: segment.mode,
        label: segment.label,
        seconds: (total?.seconds ?? 0) + seconds,
      });
    });
  });
  return [...totals.values()].toSorted((a, b) => b.seconds - a.seconds);
}
