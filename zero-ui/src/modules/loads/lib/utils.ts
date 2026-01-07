import { formatFixed, formatInt } from "@/modules/common/lib/utils";
import { NumRangeId, Range, ReferenceThresholds, VariableState, VariableUnit } from "../types";

export const formatLoad = (value: number | undefined, type: VariableUnit): string => {
  if (value === undefined) return "-";

  if (type === VariableUnit.Percentage) {
    // Values from backend are ratios
    return formatInt(value * 100);
  }

  return formatFixed(1, value);
};

export const getLoadState = (
  value?: number,
  thresholds?: Partial<ReferenceThresholds>,
): VariableState => {
  if (value === undefined) return VariableState.Unknown;

  if (!thresholds) return VariableState.Neutral;

  if (thresholds.alarmLow !== undefined && value < thresholds.alarmLow) {
    return VariableState.Alarm;
  }

  if (thresholds.alarmHigh !== undefined && value > thresholds.alarmHigh) {
    return VariableState.Alarm;
  }

  if (thresholds.warningLow !== undefined && value < thresholds.warningLow) {
    return VariableState.Warning;
  }

  if (thresholds.warningHigh !== undefined && value > thresholds.warningHigh) {
    return VariableState.Warning;
  }

  return VariableState.Neutral;
};

export const toNumRangeId = (from: number, to: number): NumRangeId =>
  `[${from},${to === Infinity ? "" : to})`;

export const toRange = (...values: number[]): Range[] =>
  values
    .toSorted((a, b) => a - b)
    .slice(0, -1)
    .map((from, i) => ({
      from,
      to: values[i + 1],
      id: toNumRangeId(from, values[i + 1]),
    }));
