import { client } from "@/modules/thrapp/graphql/client";
import { createTestingPinia } from "@pinia/testing";
import { setActivePinia } from "pinia";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { nextTick } from "vue";
import { ComponentRecord } from "../lib/consts";
import { DHW_MIMIC_QUERY, PVT_MIMIC_QUERY } from "../lib/queries.consts";
import { useThrsHistory } from "./history";

vi.mock("@/modules/thrapp/graphql/client", () => ({
  client: { mutation: vi.fn(), query: vi.fn() },
  context: {},
}));

const respond = (data: unknown) => ({ toPromise: () => Promise.resolve({ data }) }) as never;

describe("THRS history store", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    localStorage.clear();
    vi.mocked(client.query)
      .mockReset()
      .mockReturnValue(respond({ modules: {} }));
    setActivePinia(createTestingPinia({ stubActions: false }));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("does not query without an active query", async () => {
    useThrsHistory();

    await vi.advanceTimersByTimeAsync(10_000);

    expect(client.query).not.toHaveBeenCalled();
  });

  it("runs the active query when it changes and every five seconds", async () => {
    vi.setSystemTime(new Date("2026-10-27T12:00:00Z"));
    vi.mocked(client.query).mockReturnValue(respond({ modules: { dhw: {} } }));
    const history = useThrsHistory();

    history.activeQuery = DHW_MIMIC_QUERY;
    await vi.advanceTimersByTimeAsync(5000);

    expect(client.query).toHaveBeenCalledTimes(2);
    expect(client.query).toHaveBeenLastCalledWith(
      DHW_MIMIC_QUERY,
      {},
      {
        requestPolicy: "network-only",
      },
    );
    expect(history.data).toEqual({ modules: { dhw: {} } });
    expect(history.lastUpdate).toBe(new Date("2026-10-27T12:00:05Z").getTime());
  });

  it("drops the data of the previous query and late responses to it", async () => {
    let resolveFirst!: (value: unknown) => void;
    vi.mocked(client.query)
      .mockReturnValueOnce({
        toPromise: () => new Promise((resolve) => (resolveFirst = resolve)),
      } as never)
      .mockReturnValueOnce({ toPromise: () => new Promise(() => {}) } as never);
    const history = useThrsHistory();
    history.data = { modules: { dhw: {} } } as never;

    history.activeQuery = DHW_MIMIC_QUERY;
    await nextTick();
    history.activeQuery = PVT_MIMIC_QUERY;
    await nextTick();
    resolveFirst({ data: { modules: { dhw: {} } } });
    await vi.advanceTimersByTimeAsync(0);

    expect(vi.mocked(client.query).mock.calls[1][0]).toBe(PVT_MIMIC_QUERY);
    expect(history.data).toBeUndefined();
  });

  it("drops late responses once the active query is cleared", async () => {
    let resolveFirst!: (value: unknown) => void;
    vi.mocked(client.query).mockReturnValueOnce({
      toPromise: () => new Promise((resolve) => (resolveFirst = resolve)),
    } as never);
    const history = useThrsHistory();

    history.activeQuery = DHW_MIMIC_QUERY;
    await nextTick();
    history.activeQuery = undefined;
    await nextTick();
    resolveFirst({ data: { modules: { dhw: {} } } });
    await vi.advanceTimersByTimeAsync(0);

    expect(history.data).toBeUndefined();
    expect(history.lastUpdate).toBeNull();
  });

  it("sends mutations through the THRS client", async () => {
    const result = { data: { ok: true } };
    vi.mocked(client.mutation).mockReturnValue({
      toPromise: () => Promise.resolve(result),
    } as never);

    await expect(useThrsHistory().mutate("mutation { x }", { input: 1 })).resolves.toBe(result);
    expect(client.mutation).toHaveBeenCalledWith("mutation { x }", { input: 1 });
  });

  describe("getHistory", () => {
    const timestamp = new Date("2026-10-27T12:00:00Z");
    const components = {
      pump1: { flow: { value: 0.4, timestamp } },
      pump2: { flow: { value: 0.6, timestamp }, on: { value: true, timestamp } },
      valve: { setpoint: { value: 1, timestamp } },
    } as unknown as Record<string, ComponentRecord>;

    it("returns one series per component that has the field", () => {
      expect(useThrsHistory().getHistory(components, "flow")).toEqual([
        { name: "pump1", data: [[timestamp, 0.4]] },
        { name: "pump2", data: [[timestamp, 0.6]] },
      ]);
    });

    it("returns no series without data", () => {
      expect(useThrsHistory().getHistory(undefined, "flow")).toEqual([]);
    });
  });
});
