import { createTestingPinia } from "@pinia/testing";
import { createUseQueryFake } from "@tests/lib/urql";
import { useClientHandle, useQuery } from "@urql/vue";
import { DocumentNode, print } from "graphql";
import { setActivePinia } from "pinia";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useAutomationStore } from "./automation";

vi.mock(import("@urql/vue"), async (importOriginal) => ({
  ...(await importOriginal()),
  useQuery: vi.fn(),
  useClientHandle: vi.fn(),
}));

vi.mock("@/modules/thrapp/graphql/client", () => ({
  mqttGraphqlContext: { url: "/api/mqtt-graphql/graphql" },
}));

const queries = createUseQueryFake();
const mutation = vi.fn();
// the store has a single query: the control status
const controlQuery = () => queries.resultOf(vi.mocked(useQuery).mock.calls[0][0].query);

describe("automation store", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    queries.reset();
    vi.mocked(useQuery).mockReset().mockImplementation(queries.useQuery);
    vi.mocked(useClientHandle).mockReturnValue({ client: { mutation } } as never);
    mutation.mockReset().mockResolvedValue({ data: {} });
    setActivePinia(createTestingPinia({ stubActions: false }));
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("polls the control status on the MQTT GraphQL API every five seconds", () => {
    useAutomationStore();

    expect(vi.mocked(useQuery).mock.calls[0][0].context).toEqual({
      url: "/api/mqtt-graphql/graphql",
    });

    vi.advanceTimersByTime(10_000);

    expect(controlQuery().executeQuery).toHaveBeenCalledTimes(2);
    expect(controlQuery().executeQuery).toHaveBeenCalledWith({ requestPolicy: "network-only" });
  });

  it("rebuilds the control status from the automation modes and the devices' AMCS modes", () => {
    const automation = useAutomationStore();

    controlQuery().data.value = {
      thrs: {
        controller: {
          dhw: {
            automationMode: { mode: "AUTOMATIC" },
            controlMode: { boostingMode: "idle", fillingMode: "filling" },
          },
          // A control mode left over from before the switch to manual.
          thrusters: { automationMode: { mode: "MANUAL" }, controlMode: { mode: "warmup" } },
          consumers: { automationMode: { mode: "AUTOMATIC" } },
        },
      },
      marpower: { _500000Thrs: { dhw: { mode: { mode: { value: "EXTERNAL" } } } } },
    };

    expect(automation.control?.modules.dhw).toEqual({
      controlMode: {
        automatic: true,
        automaticMode: { boostingMode: "idle", fillingMode: "filling" },
      },
      sensorValues: { mode: { mode: { value: "EXTERNAL" } } },
    });
    expect(automation.control?.modules.thrusters).toEqual({
      controlMode: { automatic: false, automaticMode: null },
      sensorValues: { mode: undefined },
    });
    // Consumers' automatic mode has no fields and none of its devices has an AMCS mode.
    expect(automation.control?.modules.consumers).toEqual({
      controlMode: { automatic: true, automaticMode: null },
      sensorValues: {},
    });
  });

  it("leaves a module's control mode unknown until it has published an automation mode", () => {
    const automation = useAutomationStore();

    controlQuery().data.value = {
      thrs: { controller: { pcm: { automationMode: null, controlMode: null } } },
      marpower: { _500000Thrs: { pcm: { mode: { mode: { value: "MANUAL" } } } } },
    };

    expect(automation.control?.modules.pcm.controlMode).toBeNull();
    expect(automation.control?.modules.dc.controlMode).toBeNull();
    expect(automation.control?.modules.consumers.controlMode).toBeNull();
  });

  it("has no control status before the first response", () => {
    const automation = useAutomationStore();

    expect(automation.control).toBeUndefined();
  });

  it("switches a module's automation mode and then reloads the control status", async () => {
    const automation = useAutomationStore();

    await automation.setAutomatedControl("dhw")(true);

    const [query, variables, context] = mutation.mock.lastCall as [DocumentNode, unknown, unknown];
    expect(print(query)).toContain("dhw {");
    expect(print(query)).toMatch(/automationMode\(input: \$input\) \{\s+mode\s+\}/);
    expect(variables).toEqual({ input: { mode: "AUTOMATIC" } });
    expect(context).toEqual({ url: "/api/mqtt-graphql/graphql" });
    expect(controlQuery().executeQuery).toHaveBeenCalledOnce();
    expect(automation.isProcessing).toBe(false);
  });

  it("sends MANUAL to switch a module to manual control", async () => {
    const automation = useAutomationStore();

    await automation.setAutomatedControl("pvt")(false);

    expect(mutation.mock.lastCall?.[1]).toEqual({ input: { mode: "MANUAL" } });
  });

  it("refuses a module without a controller", () => {
    const automation = useAutomationStore();

    expect(() => automation.setAutomatedControl("cooling")).toThrow("cooling has no controller");
  });

  it("ignores a switch while another one is still being processed", async () => {
    const automation = useAutomationStore();
    mutation.mockReturnValue(new Promise(() => {}));

    void automation.setAutomatedControl("dhw")(true);
    await automation.setAutomatedControl("pvt")(false);

    expect(automation.isProcessing).toBe(true);
    expect(mutation).toHaveBeenCalledOnce();
  });

  it("logs a failed switch and is ready for the next one", async () => {
    const consoleError = vi.spyOn(console, "error").mockImplementation(() => {});
    const automation = useAutomationStore();
    mutation.mockRejectedValueOnce(new Error("Network down"));

    await automation.setAutomatedControl("dhw")(true);

    expect(consoleError).toHaveBeenCalled();
    expect(automation.isProcessing).toBe(false);
    consoleError.mockRestore();
  });
});
