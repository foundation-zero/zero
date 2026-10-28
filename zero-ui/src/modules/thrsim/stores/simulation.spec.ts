import { AmcsControlMode } from "@/modules/thrapp/types/thrs";
import { client as thrsimClient } from "@/modules/thrsim/graphql/client";
import { createTestingPinia } from "@pinia/testing";
import { createUseQueryFake } from "@tests/lib/urql";
import { useClientHandle, useQuery } from "@urql/vue";
import { DocumentNode, print } from "graphql";
import { setActivePinia } from "pinia";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { QUERY_ALL } from "../lib/consts";
import { SimulationStatus, STATUS_QUERY, useSimulationStore } from "./simulation";

vi.mock(import("@urql/vue"), async (importOriginal) => ({
  ...(await importOriginal()),
  useQuery: vi.fn(),
  useClientHandle: vi.fn(),
}));

// used by the history store, which the simulation store reads and mutates through
vi.mock("@/modules/thrsim/graphql/client", () => ({
  client: { mutation: vi.fn() },
  context: {},
}));

const queries = createUseQueryFake();
const statusQuery = () => queries.resultOf<SimulationStatus>(STATUS_QUERY);
const historyQuery = () => queries.resultOf(QUERY_ALL);
const mutation = vi.fn();
const historyMutation = vi.fn();

const withInputs = (inputs: Record<string, unknown>) => {
  historyQuery().data.value = { simulation: { inputs } };
};

describe("simulation store", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    localStorage.clear();
    queries.reset();
    vi.mocked(useQuery).mockImplementation(queries.useQuery);
    vi.mocked(useClientHandle).mockReturnValue({ client: { mutation } } as never);
    vi.mocked(thrsimClient.mutation).mockImplementation(
      (...args) => ({ toPromise: () => historyMutation(...args) }) as never,
    );
    mutation.mockReset().mockResolvedValue({ data: {} });
    historyMutation.mockReset().mockResolvedValue({ data: {} });
    setActivePinia(createTestingPinia({ stubActions: false }));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it.each([
    { status: "available", isAvailable: true, isRunning: false, isStepping: false },
    { status: "running", isAvailable: false, isRunning: true, isStepping: false },
    { status: "stepping", isAvailable: false, isRunning: false, isStepping: true },
  ] as const)("reports a $status simulation", ({ status, ...flags }) => {
    const simulation = useSimulationStore();

    statusQuery().data.value = { simulation: { status, time: 0 } };

    expect(simulation).toMatchObject(flags);
  });

  it("derives the simulation type from the inputs' GraphQL type name", () => {
    const simulation = useSimulationStore();

    withInputs({ __typename: "HighTemperatureSimulationInputs" });

    expect(simulation.activeSimulationType).toBe("highTemperature");
  });

  it("plays at the given rate and then reloads the status", async () => {
    const simulation = useSimulationStore();

    await simulation.play(2);

    const [query, variables] = mutation.mock.lastCall as [DocumentNode, unknown];
    expect(print(query)).toContain("simulationPlay(playbackRate: $value)");
    expect(variables).toEqual({ value: 2 });
    expect(statusQuery().executeQuery).toHaveBeenCalledWith({ requestPolicy: "network-only" });
  });

  describe("advisory mode", () => {
    it("is on when the simulated AMCS hands over control", () => {
      const simulation = useSimulationStore();

      withInputs({ mode: { mode: { value: AmcsControlMode.External } } });
      expect(simulation.isAdvisory).toBe(true);

      withInputs({ mode: { mode: { value: AmcsControlMode.Manual } } });
      expect(simulation.isAdvisory).toBe(false);
    });

    it.each([
      { enabled: true, mode: AmcsControlMode.External },
      { enabled: false, mode: AmcsControlMode.Manual },
    ])("sets the AMCS mode to $mode when enabled=$enabled", async ({ enabled, mode }) => {
      const simulation = useSimulationStore();
      withInputs({ __typename: "ThrustersSimulationInputs" });

      await simulation.setAdvisory(enabled);

      const [query, variables] = historyMutation.mock.lastCall as [string, unknown];
      expect(query).toContain("thrustersSimulationSetMode(value: $input)");
      expect(variables).toEqual({ input: { mode } });
      expect(historyQuery().executeQuery).toHaveBeenCalled();
      expect(simulation.advisoryError).toBeNull();
    });

    it("shows why switching failed", async () => {
      const simulation = useSimulationStore();
      withInputs({ __typename: "ThrustersSimulationInputs" });
      historyMutation.mockResolvedValue({ error: { message: "Simulation not running" } });

      await simulation.setAdvisory(true);

      expect(simulation.advisoryError).toBe("Simulation not running");
      expect(simulation.isProcessing).toBe(false);
    });

    it("does nothing while no simulation is loaded", async () => {
      await useSimulationStore().setAdvisory(true);

      expect(historyMutation).not.toHaveBeenCalled();
    });
  });
});
