import { ModeBadgeMode } from "@/modules/thrapp/mimics/components/mode-badge/mode-badge.consts";
import { describe, expect, it } from "vitest";
import { formatAge, formatReading } from "./latest-values-table/latest-values-table.utils";
import { donutArcs } from "./state-distribution/state-distribution.utils";
import { fitsLabel, placeSegments } from "./state-timeline/state-timeline.utils";
import { showGroup, toggleShown, trendOption, withAlpha } from "./trend-chart/trend-chart.utils";

const range = { start: 0, end: 100 };

describe("donutArcs", () => {
  it("splits the ring by share, one arc after the other", () => {
    const [first, second] = donutArcs([3, 1]);
    const circumference = 2 * Math.PI * 40;
    expect(first.dashoffset).toBeCloseTo(0);
    expect(second.dashoffset).toBeCloseTo(-0.75 * circumference);
    expect(Number(first.dasharray.split(" ")[0])).toBeCloseTo(0.75 * circumference - 1.2);
  });

  it("draws a single state as a full ring and nothing for no time", () => {
    expect(Number(donutArcs([5])[0].dasharray.split(" ")[0])).toBeCloseTo(2 * Math.PI * 40);
    expect(donutArcs([0, 0])).toEqual([]);
  });
});

describe("placeSegments", () => {
  const segment = (start: number, end: number) => ({
    state: "idle",
    label: "Idle",
    mode: ModeBadgeMode.Idle,
    start,
    end,
  });

  it("clips to the range and drops what lies outside it", () => {
    const placed = placeSegments([segment(-20, 30), segment(30, 120), segment(150, 160)], range);
    expect(placed.map(({ left, width }) => [left, width])).toEqual([
      [0, 30],
      [30, 70],
    ]);
  });

  it("hides labels that don't fit", () => {
    expect(fitsLabel("Idle", 60)).toBe(true);
    expect(fitsLabel("Boosting HP", 60)).toBe(false);
  });
});

describe("latest values", () => {
  it("formats readings with at most two decimals and a unit", () => {
    expect(formatReading(12.3456, "°C")).toBe((12.35).toLocaleString() + " °C");
    expect(formatReading(null, "L")).toBe("–");
  });

  it("shows the largest whole unit of an age", () => {
    expect(formatAge(12_400)).toBe("12 s");
    expect(formatAge(5 * 60_000 + 3_000)).toBe("5 min");
    expect(formatAge(26 * 3_600_000)).toBe("1 d");
  });
});

describe("trendOption", () => {
  const colors = {
    text: "rgba(1, 2, 3, 1)",
    grid: "rgba(4, 5, 6, 1)",
    limit: "rgba(7, 8, 9, 1)",
    bands: { [ModeBadgeMode.Boosting]: "rgba(10, 11, 12, 1)" },
  };
  const input = {
    lines: [
      { name: "tank2", points: [[10, 1] as [number, number]] },
      { name: "tank1", points: [[10, 2] as [number, number]] },
    ],
    hidden: new Set<string>(),
    layers: [
      {
        bands: [{ label: "Boosting", mode: ModeBadgeMode.Boosting, start: 20, end: 40 }],
        labelAt: "top" as const,
      },
    ],
    limits: {},
    range,
    unit: "°C",
    colors,
    mode: "light" as const,
  };

  it("draws a line per visible device behind the faint mode bands", () => {
    const option = trendOption({ ...input, hidden: new Set(["tank2"]) });
    const series = option.series as { name?: string; markArea?: { data: unknown[][] } }[];
    expect(series.map((item) => item.name).filter(Boolean)).toEqual(["tank1"]);
    const [[band]] = series[0].markArea!.data as { itemStyle: { color: string } }[][];
    expect(band.itemStyle.color).toBe("rgba(10, 11, 12, 0.07)");
  });

  it("draws the range between the limits as rectangles held to the end of the range", () => {
    const option = trendOption({
      ...input,
      limits: {
        lower: { name: "Minimum", points: [[0, 50]] },
        upper: { name: "Maximum", points: [[0, 65]] },
      },
    });
    const ids = (option.series as { id?: string; name?: string }[]).map(
      (item) => item.id ?? item.name,
    );
    expect(ids).toEqual([
      "band-0",
      "band-limits",
      "band-limit-Minimum",
      "band-limit-Maximum",
      "tank2",
      "tank1",
    ]);
    const area = (option.series as { markArea?: { data: unknown[] } }[])[1].markArea!.data;
    expect(area).toEqual([
      [
        { xAxis: range.start, yAxis: 50 },
        { xAxis: range.end, yAxis: 65 },
      ],
    ]);
  });

  it("labels a second overlay at the bottom", () => {
    const option = trendOption({
      ...input,
      layers: [...input.layers, { ...input.layers[0], labelAt: "bottom" }],
    });
    const series = option.series as { markArea?: { data: { label: { position: string } }[][] } }[];
    expect(series[1].markArea!.data[0][0].label.position).toBe("insideBottom");
  });

  it("stacks areas, or fills under lines that overlap", () => {
    const stacked = trendOption({ ...input, kind: "stacked" }).series as { stack?: string }[];
    expect(stacked.slice(-2).map((item) => item.stack)).toEqual(["total", "total"]);
    const area = trendOption({ ...input, kind: "area" }).series as {
      stack?: string;
      areaStyle?: { opacity: number };
    }[];
    expect(area.slice(-2).map((item) => [item.stack, item.areaStyle?.opacity])).toEqual([
      [undefined, 0.2],
      [undefined, 0.2],
    ]);
  });

  type Tooltip = { formatter: (params: unknown) => string };
  const tooltipOf = (option: ReturnType<typeof trendOption>) =>
    (option.tooltip as Tooltip).formatter;
  const hovered = (time: number, values: [string, number | null][]) => [
    { seriesId: "band-0", seriesName: "", value: [time, null], axisValue: time },
    ...values.map(([name, value]) => ({
      seriesName: name,
      value: [time, value],
      color: "red",
      axisValue: time,
    })),
  ];

  it("lists the hovered values with their unit, skipping bands and missing values", () => {
    const html = tooltipOf(trendOption(input))(
      hovered(Date.parse("2026-11-10T09:30:00"), [
        ["Tank <1>", 48.375],
        ["tank2", null],
      ]),
    );
    expect(html).toContain("Tank &lt;1&gt;");
    expect(html).toContain("48.38 °C");
    expect(html).not.toContain("tank2");
  });

  it("names the period a point averages, and sums stacked sources", () => {
    const time = Date.parse("2026-11-10T09:30:00");
    const html = tooltipOf(
      trendOption({ ...input, unit: "kW", kind: "stacked", binWidth: 600_000, totalLabel: "Sum" }),
    )(
      hovered(time, [
        ["HT", 2],
        ["DC", 3.5],
      ]),
    );
    // The point sits in the middle of its 10-minute period: 09:25 to 09:35.
    const short = (at: string) =>
      new Date(Date.parse(at)).toLocaleTimeString(undefined, { timeStyle: "short" });
    expect(html).toContain(short("2026-11-10T09:25:00"));
    expect(html).toContain(short("2026-11-10T09:35:00"));
    expect(html).toMatch(/Sum<\/span><span class="tabular-nums">5.5 kW/);
  });

  it("shows nothing when only bands are hovered", () => {
    expect(tooltipOf(trendOption(input))(hovered(0, []).slice(0, 1))).toBe("");
  });

  it("shows one line on a first click, then adds and removes, and shows all when complete", () => {
    const all = ["a", "b", "c"];
    const first = toggleShown(null, "a", all);
    expect([...first!]).toEqual(["a"]);
    const second = toggleShown(first, "b", all);
    expect([...second!]).toEqual(["a", "b"]);
    expect(toggleShown(second, "c", all)).toBeNull();
    expect(toggleShown(first, "a", all)).toBeNull();
  });

  it("shows only a group, and all again when that group alone is shown", () => {
    const group = showGroup(null, ["a", "b"]);
    expect([...group!]).toEqual(["a", "b"]);
    expect(showGroup(group, ["b", "a"])).toBeNull();
    expect(showGroup(new Set(["c"]), ["a"])).toEqual(new Set(["a"]));
  });

  it("replaces the alpha of an rgba colour", () => {
    expect(withAlpha("rgba(1, 2, 3, 1)", 0.5)).toBe("rgba(1, 2, 3, 0.5)");
    expect(withAlpha("rgb(1, 2, 3)", 0.5)).toBe("rgba(1, 2, 3, 0.5)");
  });
});
