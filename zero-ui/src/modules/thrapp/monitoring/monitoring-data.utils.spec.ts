import { flushPromises } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ref } from "vue";
import { MonitoringMetric, MonitoringSignal } from "./monitoring.consts";

const { query } = vi.hoisted(() => ({ query: vi.fn() }));
vi.mock("@/modules/thrapp/monitoring/monitoring.client", () => ({
  client: { query },
  context: {},
}));

const { useMonitoringSeries, useMonitoringStates } = await import("./monitoring-data.utils");

const MINUTE = 60_000;
const END = Date.parse("2026-11-10T12:00:00Z");
const iso = (time: number) => new Date(time).toISOString();

const respond = (data: unknown) => query.mockReturnValueOnce({ toPromise: async () => ({ data }) });

const timeline = () => ({
  resolved: ref({ start: END - 60 * MINUTE, end: END }),
  version: ref(0),
  now: ref(END),
  live: ref(true),
});

const series = (times: number[], values: number[], binSeconds = 10) => ({
  monitoringSeries: [
    {
      metric: MonitoringMetric.Temperature,
      unit: "°C",
      step: false,
      binSeconds,
      devices: [{ device: "tank1", yardTag: null, times: times.map(iso), values, latest: null }],
    },
  ],
});

describe("useMonitoringSeries", () => {
  beforeEach(() => query.mockReset());

  it("loads the range, then refreshes only its tail with the same bin size", async () => {
    const shared = timeline();
    respond(series([END - 2 * MINUTE, END - MINUTE], [1, 2]));
    const { data } = useMonitoringSeries(shared, {
      module: "DHW",
      metrics: [MonitoringMetric.Temperature],
    });
    await flushPromises();
    expect(data.value[0].devices[0].values).toEqual([1, 2]);

    respond(series([END - MINUTE, END], [3, 4]));
    shared.resolved.value = { start: END - 59 * MINUTE, end: END + MINUTE };
    shared.now.value = END + MINUTE;
    await flushPromises();

    const [, variables] = query.mock.calls[1];
    expect(variables).toMatchObject({
      start: iso(END - 20_000),
      end: iso(END + MINUTE),
      binSeconds: 10,
    });
    expect(data.value[0].devices[0].values).toEqual([1, 3, 4]);
  });

  it("does not refresh a range that ends in the past", async () => {
    const shared = timeline();
    shared.live.value = false;
    respond(series([END - MINUTE], [1]));
    useMonitoringSeries(shared, { module: "DHW", metrics: [MonitoringMetric.Temperature] });
    await flushPromises();
    shared.now.value = END + MINUTE;
    await flushPromises();
    expect(query).toHaveBeenCalledTimes(1);
  });

  it("reports an error and keeps the previous data", async () => {
    const shared = timeline();
    respond(series([END - MINUTE], [1]));
    const { data, error } = useMonitoringSeries(shared, {
      module: "DHW",
      metrics: [MonitoringMetric.Temperature],
    });
    await flushPromises();
    query.mockReturnValueOnce({ toPromise: async () => ({ error: new Error("timed out") }) });
    shared.now.value = END + MINUTE;
    await flushPromises();
    expect(error.value).toBe("timed out");
    expect(data.value[0].devices[0].values).toEqual([1]);
  });
});

describe("useMonitoringStates", () => {
  beforeEach(() => query.mockReset());

  it("reloads in full when the range changes", async () => {
    const shared = timeline();
    const states = (state: string) => ({
      monitoringStates: [
        {
          signal: MonitoringSignal.BoostingMode,
          segments: [{ state, start: iso(END - 30 * MINUTE), end: iso(END) }],
        },
      ],
    });
    respond(states("idle"));
    const { data } = useMonitoringStates(shared, {
      module: "DHW",
      signals: [MonitoringSignal.BoostingMode],
    });
    await flushPromises();
    respond(states("filling"));
    shared.version.value++;
    await flushPromises();
    expect(data.value[0].segments.map(({ state }) => state)).toEqual(["filling"]);
    expect(query.mock.calls[1][1]).toMatchObject({ start: iso(END - 60 * MINUTE) });
  });
});
