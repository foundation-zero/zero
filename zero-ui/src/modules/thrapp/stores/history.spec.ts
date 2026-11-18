import { client, mqttGraphqlClient } from "@/modules/thrapp/graphql/client";
import { createTestingPinia } from "@pinia/testing";
import { setActivePinia } from "pinia";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { nextTick } from "vue";
import { ComponentRecord } from "../lib/consts";
import { DHW_MIMIC_QUERY, PVT_MIMIC_QUERY } from "../lib/queries.consts";
import { useThrsHistory } from "./history";

vi.mock("@/modules/thrapp/graphql/client", () => ({
  client: { mutation: vi.fn() },
  mqttGraphqlClient: { query: vi.fn() },
  mqttGraphqlContext: {},
}));

const respond = (data: unknown) => ({ toPromise: () => Promise.resolve({ data }) }) as never;

const dhwPump = { flow: { value: 0.5, timestamp: "2026-10-27T12:00:00Z" } };

/** The MQTT GraphQL API's answer: the dhw pump under its alias, nested as the API has it. */
const dhwResponse = {
  marpower: { _500000Thrs: { dhw: { dhwPump } } },
};

describe("THRS history store", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    localStorage.clear();
    vi.mocked(mqttGraphqlClient.query).mockReset().mockReturnValue(respond({}));
    setActivePinia(createTestingPinia({ stubActions: false }));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("does not query without an active query", async () => {
    useThrsHistory();

    await vi.advanceTimersByTimeAsync(10_000);

    expect(mqttGraphqlClient.query).not.toHaveBeenCalled();
  });

  it("runs the active query on the MQTT GraphQL API when it changes and every five seconds", async () => {
    vi.setSystemTime(new Date("2026-10-27T12:00:00Z"));
    vi.mocked(mqttGraphqlClient.query).mockReturnValue(respond(dhwResponse));
    const history = useThrsHistory();

    history.activeQuery = DHW_MIMIC_QUERY;
    await vi.advanceTimersByTimeAsync(5000);

    expect(mqttGraphqlClient.query).toHaveBeenCalledTimes(2);
    expect(mqttGraphqlClient.query).toHaveBeenLastCalledWith(
      DHW_MIMIC_QUERY,
      {},
      {
        requestPolicy: "network-only",
      },
    );
    expect(history.data?.modules.dhw.sensorValues).toEqual({ dhwPump });
    expect(history.lastUpdate).toBe(new Date("2026-10-27T12:00:05Z").getTime());
  });

  it("drops the data of the previous query and late responses to it", async () => {
    let resolveFirst!: (value: unknown) => void;
    vi.mocked(mqttGraphqlClient.query)
      .mockReturnValueOnce({
        toPromise: () => new Promise((resolve) => (resolveFirst = resolve)),
      } as never)
      .mockReturnValueOnce({ toPromise: () => new Promise(() => {}) } as never);
    const history = useThrsHistory();
    history.data = { modules: {} } as never;

    history.activeQuery = DHW_MIMIC_QUERY;
    await nextTick();
    history.activeQuery = PVT_MIMIC_QUERY;
    await nextTick();
    resolveFirst({ data: dhwResponse });
    await vi.advanceTimersByTimeAsync(0);

    expect(vi.mocked(mqttGraphqlClient.query).mock.calls[1][0]).toBe(PVT_MIMIC_QUERY);
    expect(history.data).toBeUndefined();
  });

  it("drops late responses once the active query is cleared", async () => {
    let resolveFirst!: (value: unknown) => void;
    vi.mocked(mqttGraphqlClient.query).mockReturnValueOnce({
      toPromise: () => new Promise((resolve) => (resolveFirst = resolve)),
    } as never);
    const history = useThrsHistory();

    history.activeQuery = DHW_MIMIC_QUERY;
    await nextTick();
    history.activeQuery = undefined;
    await nextTick();
    resolveFirst({ data: dhwResponse });
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
