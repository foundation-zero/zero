import { formatFixed, formatInt, formatNumber } from "@/modules/common/lib/utils";
import { NumRangeId, Range, ReferenceThresholds, VariableState, VariableUnit } from "../types";

// Rounds like formatFixed, so a split load and a formatted load show the same digits.
const roundLoad = (digits: number, value: number): number =>
  Number(formatNumber(digits, { useGrouping: false })(value));

export const getLoadFractionDigits = (value: number): number =>
  Math.abs(roundLoad(2, value)) < 1 ? 2 : 1;

export const splitLoad = (value: number) => {
  const fractionDigits = getLoadFractionDigits(value);
  const roundedValue = roundLoad(fractionDigits, value);
  const [integer, fraction] = Math.abs(roundedValue).toFixed(fractionDigits).split(".");

  return {
    sign: roundedValue < 0 ? "-" : "",
    integer: Number(integer),
    fraction: Number(fraction),
    fractionDigits,
  };
};

export const formatLoad = (value: number | undefined | null, type: VariableUnit): string => {
  if (value == undefined) return "-";

  if (type === VariableUnit.Ratio) {
    // Values from backend are ratios
    return formatInt(value * 100);
  }

  if (type === VariableUnit.Mm) {
    return formatInt(value);
  }

  if (type === VariableUnit.Tonne) {
    return formatFixed(getLoadFractionDigits(value), value);
  }

  return formatFixed(1, value);
};

export const formatLoadFn = (type: VariableUnit) => (value: number | undefined | null) =>
  formatLoad(value, type);

export const getLoadState = (
  value?: number | null,
  thresholds?: Partial<ReferenceThresholds>,
): VariableState => {
  if (value == undefined) return VariableState.Unknown;

  if (!thresholds) return VariableState.Neutral;

  if (thresholds.alarmLow != undefined && value < thresholds.alarmLow) {
    return VariableState.Alarm;
  }

  if (thresholds.alarmHigh != undefined && value >= thresholds.alarmHigh) {
    return VariableState.Alarm;
  }

  if (thresholds.warningLow != undefined && value < thresholds.warningLow) {
    return VariableState.Warning;
  }

  if (thresholds.warningHigh != undefined && value >= thresholds.warningHigh) {
    return VariableState.Warning;
  }

  return VariableState.Neutral;
};

export const getAlarmMessageKey = (
  actualValue: number | null,
  thresholdValue: number | null,
): string => {
  if (actualValue == undefined || thresholdValue == undefined) {
    return "loads.dashboard.alarmValue";
  }

  return actualValue < thresholdValue
    ? "loads.dashboard.alarmBelowMin"
    : "loads.dashboard.alarmAboveMax";
};

export const toNumRangeId =
  (prefix: string) =>
  (from: number, to: number): NumRangeId =>
    `${prefix}_${from}_${to === Infinity ? "" : to}`;

export const toRange = <T extends string = NumRangeId>(
  idFn: (from: number, to: number, index: number) => T,
  ...values: number[]
): Range<T>[] =>
  values
    .toSorted((a, b) => a - b)
    .slice(0, -1)
    .map((from, i) => ({
      from,
      to: values[i + 1],
      id: idFn(from, values[i + 1], i),
    }));

export const unique = <T>(array: T[] | Record<string, T>): T[] => {
  return Array.from(new Set(Array.isArray(array) ? array : Object.values(array)));
};

export const findInRange = <T extends string>(
  value: number,
  ranges: Range<T>[],
): Range<T> | undefined => ranges.find(({ from, to }) => value >= from && value < to);
