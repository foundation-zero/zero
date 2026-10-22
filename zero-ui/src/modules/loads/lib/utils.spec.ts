import { describe, expect, test } from "vitest";
import { VariableUnit } from "../types";
import { formatLoad, getAlarmMessageKey } from "./utils";

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
});
