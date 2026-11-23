import { ModeBadgeMode } from "@/modules/thrapp/mimics/components/mode-badge/mode-badge.consts";
import { describe, expect, it } from "vitest";
import { MonitoringMetric, MonitoringSignal } from "../monitoring.consts";
import type { MetricSeries, StatePanelConfig } from "../monitoring.types";
import { panelRows, panelTotals } from "./state-panel/state-panel.utils";
import {
  deviceLabel,
  energyRows,
  latestRows,
  litres,
  shortDeviceName,
  stackable,
  trendLimit,
  trendLines,
  waterFlows,
  waterPeriod,
} from "./trend-panel/trend-panel.utils";

const MINUTE = 60_000;
const iso = (minutes: number) => new Date(minutes * 60_000).toISOString();
const styleOf = (_signal: string, state: string) => ({ mode: ModeBadgeMode.Idle, label: state });

const tanks: StatePanelConfig = {
  key: "tankState",
  header: "tankState",
  rows: [
    { signal: MonitoringSignal.Tank1State, label: { key: "tank", params: { number: 1 } } },
    { signal: MonitoringSignal.Tank2State, label: { key: "tank", params: { number: 2 } } },
  ],
};
const states = [
  {
    signal: MonitoringSignal.Tank1State,
    segments: [
      { state: "in use", start: iso(0), end: iso(40) },
      { state: "filling", start: iso(40), end: iso(60) },
    ],
  },
  {
    signal: MonitoringSignal.Tank2State,
    segments: [{ state: "filling", start: iso(-30), end: iso(30) }],
  },
];

describe("state panel", () => {
  it("makes one timeline row per signal", () => {
    const rows = panelRows(tanks, states, styleOf, ({ params }) => `Tank ${params?.number}`);
    expect(rows.map(({ label, segments }) => [label, segments.length])).toEqual([
      ["Tank 1", 2],
      ["Tank 2", 1],
    ]);
  });

  it("totals the time per state over all rows, clipped to the range, longest first", () => {
    const totals = panelTotals(tanks, states, { start: 0, end: 60 * 60_000 }, styleOf);
    expect(totals.map(({ state, seconds }) => [state, seconds / 60])).toEqual([
      ["filling", 50],
      ["in use", 40],
    ]);
  });
});

describe("trend panel", () => {
  const series: MetricSeries[] = [
    {
      metric: MonitoringMetric.Temperature,
      unit: "°C",
      step: false,
      binSeconds: 60,
      devices: [
        {
          device: "dhw-temperature-tank1",
          yardTag: "50001038-45",
          times: [iso(0), iso(1)],
          values: [50, 51],
          latest: { value: 51.2, timestamp: iso(1) },
        },
        { device: "dhw-pressure", yardTag: null, times: [], values: [], latest: null },
      ],
    },
    {
      metric: MonitoringMetric.MinimumTankTemperature,
      unit: "°C",
      step: true,
      binSeconds: null,
      devices: [
        {
          device: "minimum_tank_temperature",
          yardTag: null,
          times: [iso(0), iso(60)],
          values: [51, 51],
          latest: null,
        },
      ],
    },
  ];
  const config = {
    key: "tankTemperatures",
    metrics: [MonitoringMetric.Temperature],
    deviceLabels: { "dhw-temperature-tank1": "Tank 1" },
  };

  it("names devices by their label, else by yard tag and name", () => {
    expect(deviceLabel(series[0].devices[0], config)).toBe("Tank 1");
    expect(deviceLabel(series[0].devices[0], { ...config, deviceLabels: {} })).toBe(
      "[50001038-45] dhw-temperature-tank1",
    );
    expect(deviceLabel(series[0].devices[1], config)).toBe("dhw-pressure");
  });

  it("turns a metric into lines, latest values and a limit", () => {
    expect(trendLines(series, MonitoringMetric.Temperature, config)[0].points).toEqual([
      [0, 50],
      [60_000, 51],
    ]);
    expect(latestRows(series, MonitoringMetric.Temperature, config)).toEqual([
      { asset: "Tank 1", shortName: "Tank 1", value: 51.2, timestamp: 60_000 },
      { asset: "dhw-pressure", shortName: "Pressure", value: null, timestamp: null },
    ]);
    expect(trendLimit(series, MonitoringMetric.MinimumTankTemperature, "Minimum")?.points).toEqual([
      [0, 51],
      [3_600_000, 51],
    ]);
    expect(trendLimit(series, MonitoringMetric.MaximumTankTemperature, "Maximum")).toBeUndefined();
  });
});

describe("heat and water usage", () => {
  const heat: MetricSeries[] = [
    {
      metric: MonitoringMetric.Heat,
      unit: "kW",
      step: false,
      binSeconds: 1800,
      devices: [
        { device: "hp", yardTag: null, times: [iso(0), iso(30)], values: [2, 4], latest: null },
        { device: "ht", yardTag: null, times: [iso(0), iso(30)], values: [10, -3], latest: null },
      ],
    },
  ];
  const config = {
    key: "heat",
    metrics: [MonitoringMetric.Heat],
    deviceLabels: { hp: "Heat pump" },
  };

  it("puts stacked lines on the same times, with gaps and power below zero as zero", () => {
    const [ht, hp] = stackable([
      {
        name: "ht",
        points: [
          [0, -3],
          [1, null],
          [2, 5],
        ],
      },
      { name: "hp", points: [[1, 2]] },
    ]);
    expect(ht.points).toEqual([
      [0, 0],
      [1, 0],
      [2, 5],
    ]);
    expect(hp.points).toEqual([
      [0, 0],
      [1, 2],
      [2, 0],
    ]);
  });

  it("adds up energy per source in kWh, the largest first", () => {
    expect(
      energyRows(heat, MonitoringMetric.Heat, config).map(({ asset, value }) => [asset, value]),
    ).toEqual([
      ["ht", 5],
      ["Heat pump", 3],
    ]);
  });

  it("derives hot water out from fresh water in less what the tanks gained", () => {
    const range = { start: 0, end: 60 * 60_000 };
    expect(waterPeriod(range)).toBe(MINUTE);
    const tank = (device: string, values: number[]) => ({
      device,
      yardTag: null,
      times: values.map((_, index) => iso(index)),
      values,
      latest: null,
    });
    const series: MetricSeries[] = [
      {
        metric: MonitoringMetric.CalculatedFlow,
        unit: "L/min",
        step: false,
        binSeconds: 60,
        devices: [tank("fresh", [0, 10, 10, 0])],
      },
      {
        metric: MonitoringMetric.Level,
        unit: "L",
        step: false,
        binSeconds: 60,
        // Filling 10 L/min while 4 L/min is drawn; then only drawing 6 L/min.
        devices: [tank("t1", [100, 103, 106, 103]), tank("t2", [50, 53, 56, 53])],
      },
    ];

    const { inflow, outflow, period } = waterFlows(series, "fresh", ["t1", "t2"], range);

    expect(inflow.slice(0, 4).map(([, value]) => value)).toEqual([0, 10, 10, 0]);
    expect(outflow.slice(0, 4).map(([, value]) => value)).toEqual([null, 4, 4, 6]);
    expect(inflow[0][0]).toBe(30_000);
    expect(litres(outflow, period)).toBe(14);
  });

  it("names devices in words, without the module and kind", () => {
    expect(shortDeviceName("dhw-temperature-hvac-exchanger-return")).toBe("HVAC exchanger return");
    expect(shortDeviceName("dhw-switch-tank1-inlet")).toBe("Tank1 inlet");
    expect(shortDeviceName("dhw-pump")).toBe("Pump");
    expect(shortDeviceName("dhw-temperature-dc-return")).toBe("DC return");
  });
});
