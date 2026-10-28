import { client } from "@/modules/thrsim/graphql/client";
import { createTestingPinia } from "@pinia/testing";
import { createUseQueryFake } from "@tests/lib/urql";
import { useQuery } from "@urql/vue";
import { setActivePinia } from "pinia";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ComponentRecord, QUERY_ALL } from "../lib/consts";
import { useThrsHistory } from "./history";

vi.mock(import("@urql/vue"), async (importOriginal) => ({
  ...(await importOriginal()),
  useQuery: vi.fn(),
}));

vi.mock("@/modules/thrsim/graphql/client", () => ({
  client: { mutation: vi.fn() },
  context: {},
}));

const queries = createUseQueryFake();
const allQuery = () => queries.resultOf(QUERY_ALL);

describe("thrsim history store", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    localStorage.clear();
    queries.reset();
    vi.mocked(useQuery).mockImplementation(queries.useQuery);
    setActivePinia(createTestingPinia({ stubActions: false }));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("refreshes every five seconds and remembers when it last did", async () => {
    vi.setSystemTime(new Date("2026-10-27T12:00:00Z"));
    const history = useThrsHistory();

    await vi.advanceTimersByTimeAsync(5000);

    expect(allQuery().executeQuery).toHaveBeenCalledOnce();
    expect(history.lastUpdate).toBe(new Date("2026-10-27T12:00:05Z").getTime());
  });

  it("sends mutations through the thrsim client", async () => {
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
