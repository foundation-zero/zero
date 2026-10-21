import { describe, expect, test } from "vitest";
import { VariableUnit } from "../types";
import { formatLoad, getAlarmMessageKey, splitLoad } from "./utils";

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
  test("shows one decimal from 1 t", () => {
    expect(formatLoad(12.43, VariableUnit.Tonne)).toBe("12.4");
    expect(formatLoad(1, VariableUnit.Tonne)).toBe("1.0");
  });

  test("shows two decimals below 1 t", () => {
    expect(formatLoad(0.75, VariableUnit.Tonne)).toBe("0.75");
    expect(formatLoad(0.05, VariableUnit.Tonne)).toBe("0.05");
    expect(formatLoad(-0.62, VariableUnit.Tonne)).toBe("-0.62");
  });

  test("shows one decimal when the value rounds up to 1 t", () => {
    expect(formatLoad(0.996, VariableUnit.Tonne)).toBe("1.0");
  });

  test("shows millimeters without decimals", () => {
    expect(formatLoad(335, VariableUnit.Mm)).toBe("335");
  });

  test("keeps one decimal for other units", () => {
    expect(formatLoad(0.75, VariableUnit.Meter)).toBe("0.8");
  });
});

describe("splitLoad", () => {
  test("splits a load from 1 t into one decimal", () => {
    expect(splitLoad(12.43)).toEqual({ sign: "", integer: 12, fraction: 4, fractionDigits: 1 });
  });

  test("splits a load below 1 t into two decimals", () => {
    expect(splitLoad(0.05)).toEqual({ sign: "", integer: 0, fraction: 5, fractionDigits: 2 });
  });

  test("keeps the sign of a negative load below 1 t", () => {
    expect(splitLoad(-0.62)).toEqual({ sign: "-", integer: 0, fraction: 62, fractionDigits: 2 });
  });

  test("keeps the sign of a negative load from 1 t", () => {
    expect(splitLoad(-1.26)).toEqual({ sign: "-", integer: 1, fraction: 3, fractionDigits: 1 });
  });

  test.each([0.995, -0.995, 9.95])("rounds %d like formatLoad", (value) => {
    const { sign, integer, fraction, fractionDigits } = splitLoad(value);

    expect(`${sign}${integer}.${String(fraction).padStart(fractionDigits, "0")}`).toBe(
      formatLoad(value, VariableUnit.Tonne),
    );
  });

  test("drops the sign when a negative load rounds to zero", () => {
    expect(splitLoad(-0.001)).toEqual({ sign: "", integer: 0, fraction: 0, fractionDigits: 2 });
  });
});
