import { describe, expect, it } from "vitest";
import { formatAlarmTime } from "./alarm-table.utils";

describe("formatAlarmTime", () => {
  const now = new Date(2026, 10, 19, 16, 0);

  it("shows only the time of day for today", () => {
    expect(formatAlarmTime(new Date(2026, 10, 19, 9, 5, 7).toISOString(), now)).toBe("09:05:07");
  });

  it("adds the date for another day", () => {
    expect(formatAlarmTime(new Date(2026, 10, 18, 23, 59, 1).toISOString(), now)).toBe(
      "18 Nov 23:59:01",
    );
  });

  it("shows a dash without a time", () => {
    expect(formatAlarmTime(null, now)).toBe("—");
  });
});
