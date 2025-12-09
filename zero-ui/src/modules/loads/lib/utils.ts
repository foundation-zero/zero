import { formatFixed, formatInt } from "@/modules/common/lib/utils";
import { ReferenceThresholds, VariableState, VariableType } from "../types";

export const formatLoad = (value: number | undefined, type: VariableType): string => {
  if (value === undefined) return "-";

  if (type === VariableType.Percentage) {
    return formatInt(value);
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
