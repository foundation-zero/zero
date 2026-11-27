import { useThrsHistory } from "@/modules/thrapp/stores/history";
import { AmcsMode } from "@/modules/thrapp/types/thrs";
import { createTestingPinia } from "@pinia/testing";
import { createUseQueryFake } from "@tests/lib/urql";
import { useClientHandle, useQuery } from "@urql/vue";
import { DocumentNode, print } from "graphql";
import { setActivePinia } from "pinia";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { SIMULATOR_QUERY } from "../lib/consts";
import { Simulator, SimulatorStatus } from "../lib/consts.types";
import { useSimulationStore } from "./simulation";

vi.mock(import("@urql/vue"), async (importOriginal) => ({
  ...(await importOriginal()),
  useQuery: vi.fn(),
  useClientHandle: vi.fn(),
}));

// used by the THRS history store, which the simulation store refreshes
vi.mock("@/modules/thrapp/graphql/client", () => ({
  context: {},
  mqttGraphqlClient: { query: vi.fn(), mutation: vi.fn() },
  mqttGraphqlContext: {},
}));

const queries = createUseQueryFake();
const simulatorQuery = () => queries.resultOf<Simulator>(SIMULATOR_QUERY);
const mutation = vi.fn();

const running: SimulatorStatus = { status: "RUNNING", mode: "thrusters", simulationTime: "" };

const withSimulator = (
  status: SimulatorStatus | null,
  simulationInputs: Record<string, unknown> = {},
) => {
  simulatorQuery().data.value = {
    thrs: { simulator: { status, simulationInputs, simulationOutputs: {} } },
  } as Simulator;
};

describe("simulation store", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    localStorage.clear();
    queries.reset();
    vi.mocked(useQuery).mockImplementation(queries.useQuery);
    vi.mocked(useClientHandle).mockReturnValue({ client: { mutation } } as never);
    mutation.mockReset().mockResolvedValue({ data: {} });
    setActivePinia(createTestingPinia({ stubActions: false }));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("polls the simulator only while polling is started", () => {
    const simulation = useSimulationStore();

    vi.advanceTimersByTime(10000);
    expect(simulatorQuery().executeQuery).not.toHaveBeenCalled();

    simulation.startPolling();
    vi.advanceTimersByTime(10000);
    expect(simulatorQuery().executeQuery).toHaveBeenCalledTimes(3);

    simulation.stopPolling();
    vi.advanceTimersByTime(10000);
    expect(simulatorQuery().executeQuery).toHaveBeenCalledTimes(3);
  });

  it.each([
    { status: "AVAILABLE", isAvailable: true, isRunning: false, isStepping: false },
    { status: "RUNNING", isAvailable: false, isRunning: true, isStepping: false },
    { status: "STEPPING", isAvailable: false, isRunning: false, isStepping: true },
  ] as const)("reports a $status simulation", ({ status, ...flags }) => {
    const simulation = useSimulationStore();

    withSimulator({ ...running, status });

    expect(simulation).toMatchObject(flags);
  });

  it("takes the simulation type from the status' mode", () => {
    const simulation = useSimulationStore();

    withSimulator({ ...running, mode: "high_temperature" });

    expect(simulation.activeSimulationType).toBe("highTemperature");
  });

  it("has no simulation without a status, as from a simulator apart from the controller", () => {
    const simulation = useSimulationStore();

    withSimulator(null, { thrustersThrusterAft: {} });

    expect(simulation.simulation).toBeUndefined();
    expect(simulation.activeSimulationType).toBeUndefined();
  });

  it("plays at the given rate and then reloads the simulator", async () => {
    const simulation = useSimulationStore();

    await simulation.play(2);

    const [query, variables] = mutation.mock.lastCall as [DocumentNode, unknown];
    expect(print(query)).toContain("status(input: $input)");
    expect(variables).toEqual({ input: { status: "RUNNING", playbackRate: 2, pauseAt: null } });
    expect(simulatorQuery().executeQuery).toHaveBeenCalledWith({ requestPolicy: "network-only" });
  });

  it("pauses the simulator now", async () => {
    await useSimulationStore().pause();

    const [, variables] = mutation.mock.lastCall as [DocumentNode, unknown];
    expect(variables).toEqual({ input: { status: "AVAILABLE", pauseAt: null } });
  });

  it("steps until the given seconds after the simulation time", async () => {
    const simulation = useSimulationStore();
    withSimulator({ ...running, status: "AVAILABLE", simulationTime: "2026-11-13T10:00:00Z" });

    await simulation.step(30);

    const [, variables] = mutation.mock.lastCall as [DocumentNode, unknown];
    expect(variables).toEqual({
      input: { status: "STEPPING", pauseAt: "2026-11-13T10:00:30.000Z" },
    });
  });

  it("does not step without a simulation time", async () => {
    await useSimulationStore().step(30);

    expect(mutation.mock.calls).toEqual([]);
  });

  describe("advisory mode", () => {
    it("is on when the simulated AMCS hands over control", () => {
      const simulation = useSimulationStore();

      withSimulator(running, { mode: { mode: { value: AmcsMode.External } } });
      expect(simulation.isAdvisory).toBe(true);

      withSimulator(running, { mode: { mode: { value: AmcsMode.Manual } } });
      expect(simulation.isAdvisory).toBe(false);
    });

    it.each([
      { enabled: true, mode: AmcsMode.External },
      { enabled: false, mode: AmcsMode.Manual },
    ])("sets the AMCS mode to $mode when enabled=$enabled", async ({ enabled, mode }) => {
      const simulation = useSimulationStore();
      const refreshHistory = vi.spyOn(useThrsHistory(), "refresh");
      withSimulator(running);

      await simulation.setAdvisory(enabled);

      const [query, variables] = mutation.mock.lastCall as [DocumentNode, unknown];
      expect(print(query)).toContain("simulationInputs(input: $input)");
      expect(variables).toEqual({
        input: { mode: { mode: { value: mode } } },
      });
      expect(refreshHistory).toHaveBeenCalled();
      expect(simulatorQuery().executeQuery).toHaveBeenCalled();
      expect(simulation.advisoryError).toBeNull();
    });

    it("shows why switching failed", async () => {
      const simulation = useSimulationStore();
      withSimulator(running);
      mutation.mockResolvedValue({ error: { message: "Simulation not running" } });

      await simulation.setAdvisory(true);

      expect(simulation.advisoryError).toBe("Simulation not running");
      expect(simulation.isProcessing).toBe(false);
    });

    it("does nothing while no simulation is loaded", async () => {
      await useSimulationStore().setAdvisory(true);

      expect(mutation).not.toHaveBeenCalled();
    });
  });
});
