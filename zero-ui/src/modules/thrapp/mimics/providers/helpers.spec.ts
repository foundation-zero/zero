import { SensorAlarms } from "@/modules/thrsim/types";
import { describe, expect, it } from "vitest";
import { MimicComponentState } from "../components";
import { componentStateFromAlarms, extractFieldValue } from "./helpers";

const stamp = <T>(value: T) => ({ value, timestamp: new Date() });

const alarms = (active: Partial<Record<keyof SensorAlarms, boolean>> = {}): SensorAlarms => ({
  anyFailureActive: stamp(active.anyFailureActive ?? false),
  anyWarningActive: stamp(active.anyWarningActive ?? false),
  feedbackFailure: stamp(active.feedbackFailure ?? false),
  externalOutOfRange: stamp(active.externalOutOfRange ?? false),
});

describe("componentStateFromAlarms", () => {
  it.each<keyof SensorAlarms>([
    "anyFailureActive",
    "anyWarningActive",
    "feedbackFailure",
    "externalOutOfRange",
  ])("overrides the state with an alarm when %s is active", (alarm) => {
    expect(componentStateFromAlarms(MimicComponentState.Manual, alarms({ [alarm]: true }))).toBe(
      MimicComponentState.Alarm,
    );
  });

  it("keeps the given state when no alarm is active", () => {
    expect(componentStateFromAlarms(MimicComponentState.Manual, alarms())).toBe(
      MimicComponentState.Manual,
    );
  });

  it("keeps the given state when there is no sensor data yet", () => {
    expect(componentStateFromAlarms(MimicComponentState.Normal)).toBe(MimicComponentState.Normal);
  });
});

describe("extractFieldValue", () => {
  const extractFlow = extractFieldValue("flow");

  it("returns the unstamped value of the field", () => {
    expect(extractFlow({ flow: stamp(0.4) })).toBe(0.4);
  });

  it("keeps falsy values instead of treating them as missing", () => {
    expect(extractFlow({ flow: stamp(0) })).toBe(0);
  });

  it("returns undefined when there is no data", () => {
    expect(extractFlow(undefined)).toBeUndefined();
  });
});
