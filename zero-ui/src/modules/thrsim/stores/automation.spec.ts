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

  it("polls the control status every five seconds", () => {
    useAutomationStore();

    vi.advanceTimersByTime(10_000);

    expect(controlQuery().executeQuery).toHaveBeenCalledTimes(2);
    expect(controlQuery().executeQuery).toHaveBeenCalledWith({ requestPolicy: "network-only" });
  });

  it("switches a module's automation mode and then reloads the control status", async () => {
    const automation = useAutomationStore();

    await automation.setAutomatedControl("dhw")(true);

    const [query, variables] = mutation.mock.lastCall as [DocumentNode, unknown];
    expect(print(query)).toContain("dhwSetAutomationMode(automatic: $value)");
    expect(variables).toEqual({ value: true });
    expect(controlQuery().executeQuery).toHaveBeenCalledOnce();
    expect(automation.isProcessing).toBe(false);
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
