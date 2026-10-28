import { describe, expect, test } from "vitest";
import { VariableState, VariableUnit } from "../types";
import {
  findInRange,
  formatLoad,
  formatLoadFn,
  getAlarmMessageKey,
  getLoadState,
  toNumRangeId,
  toRange,
  unique,
} from "./utils";

describe("getAlarmMessageKey", () => {
  test("shows only the value without a threshold", () => {
    expect(getAlarmMessageKey(12.4, null)).toBe("loads.dashboard.alarmValue");
  });

  test("shows only the value without an actual value", () => {
    expect(getAlarmMessageKey(null, 10)).toBe("loads.dashboard.alarmValue");
  });

  test("shows above max when the value exceeds the threshold", () => {
    expect(getAlarmMessageKey(12.4, 10)).toBe("loads.dashboard.alarmAboveMax");
  });

  test("shows above max when the value equals the threshold", () => {
    expect(getAlarmMessageKey(10, 10)).toBe("loads.dashboard.alarmAboveMax");
  });

  test("shows below min when the value is under the threshold", () => {
    expect(getAlarmMessageKey(0.03, 0.05)).toBe("loads.dashboard.alarmBelowMin");
  });

  test("treats a zero threshold as present", () => {
    expect(getAlarmMessageKey(-1, 0)).toBe("loads.dashboard.alarmBelowMin");
  });
});

describe("formatLoad", () => {
  test("shows millimeters without decimals", () => {
    expect(formatLoad(335, VariableUnit.Mm)).toBe("335");
  });

  test("shows ratios as percentages", () => {
    expect(formatLoad(0.425, VariableUnit.Ratio)).toBe("43");
  });

  test("shows other units with one decimal", () => {
    expect(formatLoad(12.34, VariableUnit.Tonne)).toBe("12.3");
  });

  test("shows a dash without a value", () => {
    expect(formatLoad(null, VariableUnit.Tonne)).toBe("-");
  });
});

describe("formatLoadFn", () => {
  test("formats like formatLoad for the given unit", () => {
    expect(formatLoadFn(VariableUnit.Ratio)(0.5)).toBe("50");
    expect(formatLoadFn(VariableUnit.Tonne)(2)).toBe("2.0");
    expect(formatLoadFn(VariableUnit.Tonne)(undefined)).toBe("-");
  });
});

describe("getLoadState", () => {
  const thresholds = { alarmLow: 0, warningLow: 10, warningHigh: 90, alarmHigh: 100 };

  test.each([
    [undefined, VariableState.Unknown],
    [-1, VariableState.Alarm],
    [5, VariableState.Warning],
    [50, VariableState.Neutral],
    [90, VariableState.Warning],
    [100, VariableState.Alarm],
  ])("%s is %s", (value, state) => {
    expect(getLoadState(value, thresholds)).toBe(state);
  });

  test("is neutral without thresholds", () => {
    expect(getLoadState(50)).toBe(VariableState.Neutral);
  });
});

describe("ranges", () => {
  const ranges = toRange(toNumRangeId("speed"), 0, 10, Infinity);

  test("toRange creates consecutive ranges", () => {
    expect(ranges.map(({ from, id }) => [from, id])).toEqual([
      [0, "speed_0_10"],
      [10, "speed_10_"],
    ]);
  });

  test("findInRange includes the lower bound only", () => {
    expect(findInRange(10, ranges)?.id).toBe("speed_10_");
    expect(findInRange(-1, ranges)).toBeUndefined();
  });
});

describe("unique", () => {
  test("deduplicates arrays and record values", () => {
    expect(unique([1, 1, 2])).toEqual([1, 2]);
    expect(unique({ a: "x", b: "x" })).toEqual(["x"]);
  });
});
