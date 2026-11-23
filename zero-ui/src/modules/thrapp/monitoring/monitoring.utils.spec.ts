import { describe, expect, it } from "vitest";
import { DEFAULT_SPAN, MAX_SPAN } from "./monitoring.consts";
import type { DeviceSeries, Segment } from "./monitoring.types";
import {
  customRange,
  durationParts,
  heldUntil,
  limitRects,
  mergeDeviceSeries,
  mergeSegments,
  placeAnnotations,
  presetKey,
  rangeFromQuery,
  rangeToQuery,
  resolveRange,
  seriesColor,
  shiftRange,
  stateTotals,
  timeTicks,
  withGaps,
  zoomedRange,
  zoomOut,
} from "./monitoring.utils";

const HOUR = 3_600_000;
const NOW = Date.parse("2026-11-10T12:00:00Z");
const at = (minutes: number) => new Date(NOW + minutes * 60_000).toISOString();

describe("time ranges", () => {
  it("resolves a live range to end at now", () => {
    expect(resolveRange({ span: HOUR, end: null }, NOW)).toEqual({ start: NOW - HOUR, end: NOW });
  });

  it("zooms to a dragged stretch, at least a minute long and not past now", () => {
    expect(zoomedRange({ start: NOW - HOUR, end: NOW - HOUR / 2 }, NOW)).toEqual({
      span: HOUR / 2,
      end: NOW - HOUR / 2,
    });
    expect(zoomedRange({ start: NOW - 10_000, end: NOW - 5_000 }, NOW)).toEqual({
      span: 60_000,
      end: NOW,
    });
  });

  it("reads a typed range, following now when it ends at or after now", () => {
    expect(customRange(NOW - 2 * HOUR, NOW - HOUR, NOW)).toEqual({
      range: { span: HOUR, end: NOW - HOUR },
    });
    expect(customRange(NOW - HOUR, NOW + HOUR, NOW)).toEqual({ range: { span: HOUR, end: null } });
    expect(customRange(NOW, NOW - HOUR, NOW)).toEqual({ error: "order" });
    expect(customRange(NOW - 40 * 24 * HOUR, NOW, NOW)).toEqual({ error: "tooLong" });
    expect(customRange(Number.NaN, NOW, NOW)).toEqual({ error: "invalid" });
  });

  it("shifts back by one span and returns to live at now", () => {
    const back = shiftRange({ span: HOUR, end: null }, -1, NOW);
    expect(back).toEqual({ span: HOUR, end: NOW - HOUR });
    expect(shiftRange(back, 1, NOW)).toEqual({ span: HOUR, end: null });
  });

  it("zooms out by doubling, up to the longest range", () => {
    expect(zoomOut({ span: HOUR, end: null }).span).toBe(2 * HOUR);
    expect(zoomOut({ span: MAX_SPAN, end: null }).span).toBe(MAX_SPAN);
  });

  it("names preset spans only", () => {
    expect(presetKey(6 * HOUR)).toBe("6h");
    expect(presetKey(2 * HOUR)).toBeUndefined();
  });

  it("round-trips through the URL query", () => {
    const range = { span: 7 * 24 * HOUR, end: NOW };
    expect(rangeFromQuery(rangeToQuery(range))).toEqual(range);
    expect(rangeToQuery({ span: 90 * 60_000, end: null })).toEqual({
      range: "90m",
      end: undefined,
    });
  });

  it("falls back to the default for an invalid query and caps the span", () => {
    expect(rangeFromQuery({ range: "soon", end: "never" })).toEqual({
      span: DEFAULT_SPAN,
      end: null,
    });
    expect(rangeFromQuery({ range: "90d" }).span).toBe(MAX_SPAN);
  });
});

describe("durationParts", () => {
  it("splits seconds into days, hours, minutes and seconds", () => {
    expect(durationParts(45_010)).toEqual({ days: 0, hours: 12, minutes: 30, seconds: 10 });
    expect(durationParts(90_061)).toEqual({ days: 1, hours: 1, minutes: 1, seconds: 1 });
  });
});

describe("timeTicks", () => {
  it("places round ticks inside the range", () => {
    const ticks = timeTicks({ start: NOW - 6 * HOUR + 60_000, end: NOW });
    expect(ticks.length).toBeGreaterThan(2);
    expect(ticks.length).toBeLessThanOrEqual(8);
    expect(ticks.every((tick) => tick >= NOW - 6 * HOUR && tick <= NOW)).toBe(true);
    const steps = new Set(ticks.slice(1).map((tick, index) => tick - ticks[index]));
    expect(steps.size).toBe(1);
  });
});

describe("withGaps", () => {
  it("breaks the line where samples are missing", () => {
    const times = [0, 60_000, 600_000];
    expect(withGaps(times, [1, 2, 3])).toEqual([
      [0, 1],
      [60_000, 2],
      [60_001, null],
      [600_000, 3],
    ]);
  });
});

describe("seriesColor", () => {
  it("follows the sorted device names, not the order they arrive in", () => {
    expect(seriesColor("tank2", ["tank3", "tank2"], "light")).toEqual(
      seriesColor("tank2", ["tank2", "tank3"], "light"),
    );
    expect(seriesColor("tank2", ["tank3", "tank2"], "light")).toEqual({
      color: "#2a78d6",
      dashed: false,
    });
  });

  it("dashes series past the eight palette slots", () => {
    const names = Array.from({ length: 9 }, (_, index) => `sensor-${index}`);
    expect(seriesColor("sensor-8", names, "light")).toEqual({ color: "#2a78d6", dashed: true });
  });
});

const device = (name: string, minutes: number[], values: number[]): DeviceSeries => ({
  device: name,
  yardTag: null,
  times: minutes.map(at),
  values,
  latest: null,
});

describe("mergeDeviceSeries", () => {
  it("replaces the overlapping tail and drops points before the window", () => {
    const merged = mergeDeviceSeries(
      [device("tank1", [-60, -30, -1], [1, 2, 3])],
      [device("tank1", [-1, 0], [4, 5])],
      Date.parse(at(-45)),
    );
    expect(merged).toEqual([device("tank1", [-30, -1, 0], [2, 4, 5])]);
  });

  it("keeps devices that only one side has", () => {
    const merged = mergeDeviceSeries(
      [device("tank1", [-10], [1])],
      [device("tank2", [0], [2])],
      Date.parse(at(-60)),
    );
    expect(merged.map(({ device }) => device)).toEqual(["tank1", "tank2"]);
  });
});

describe("mergeSegments", () => {
  const segment = (state: string, start: number, end: number): Segment => ({
    state,
    start: at(start),
    end: at(end),
  });

  it("clips the old tail, joins equal states and trims to the window", () => {
    const merged = mergeSegments(
      [segment("idle", -60, -20), segment("filling", -20, 0)],
      [segment("filling", -1, 1), segment("idle", 1, 2)],
      Date.parse(at(-30)),
    );
    expect(merged).toEqual([
      segment("idle", -30, -20),
      segment("filling", -20, 1),
      segment("idle", 1, 2),
    ]);
  });

  it("totals the seconds per state", () => {
    const totals = stateTotals([
      segment("idle", 0, 10),
      segment("filling", 10, 15),
      segment("idle", 15, 20),
    ]);
    expect(Object.fromEntries(totals)).toEqual({ idle: 900, filling: 300 });
  });
});

describe("limits", () => {
  const lower = {
    name: "min",
    points: [
      [0, 50],
      [20, 52],
    ] as [number, number][],
  };
  const upper = {
    name: "max",
    points: [
      [0, 65],
      [10, 67],
    ] as [number, number][],
  };

  it("splits the area between two step limits at each change and holds it to the end", () => {
    expect(limitRects(lower, upper, { start: 5, end: 30 })).toEqual([
      { start: 5, end: 10, low: 50, high: 65 },
      { start: 10, end: 20, low: 50, high: 67 },
      { start: 20, end: 30, low: 52, high: 67 },
    ]);
  });

  it("leaves out changes after the range", () => {
    expect(limitRects(lower, upper, { start: 0, end: 15 })).toEqual([
      { start: 0, end: 10, low: 50, high: 65 },
      { start: 10, end: 15, low: 50, high: 67 },
    ]);
  });

  it("holds a limit line until the end of the range", () => {
    expect(heldUntil(lower, 30)).toEqual([
      [0, 50],
      [20, 52],
      [30, 52],
    ]);
    expect(heldUntil(lower, 20)).toEqual(lower.points);
  });
});

describe("placeAnnotations", () => {
  const note = (id: string, minutes: number, kind: "CREW" | "ALARM" = "CREW") => ({
    id,
    kind,
    time: at(minutes),
    text: id,
    author: null,
    canDelete: false,
    changes: [],
  });

  it("places shown annotations inside the range by their share of it", () => {
    const range = { start: NOW, end: NOW + HOUR };
    const placed = placeAnnotations(
      [note("a", 15), note("b", 30, "ALARM"), note("c", 90), note("d", -1)],
      new Set(["CREW"]),
      range,
    );
    expect(placed.map(({ annotation, left }) => [annotation.id, left])).toEqual([["a", 25]]);
  });
});
