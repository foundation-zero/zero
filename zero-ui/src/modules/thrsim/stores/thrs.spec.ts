import { useThrsHistory } from "@/modules/thrapp/stores/history";
import { createTestingPinia } from "@pinia/testing";
import { DocumentNode, print } from "graphql";
import { setActivePinia } from "pinia";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ref } from "vue";
import { useSimulationStore } from "./simulation";
import { controlForm, simulationInputsForm } from "./thrs";

vi.mock("@/modules/thrapp/graphql/client", () => ({
  mqttGraphqlClient: { query: vi.fn(), mutation: vi.fn() },
  mqttGraphqlContext: {},
}));

// used by the simulation store, which the simulation inputs form sends through
vi.mock(import("@urql/vue"), async (importOriginal) => ({
  ...(await importOriginal()),
  useQuery: vi.fn(() => ({ data: ref(), executeQuery: vi.fn() })) as never,
  useClientHandle: vi.fn(() => ({ client: {} })) as never,
}));

const stamp = <T>(value: T) => ({ value, timestamp: new Date() });

describe("control form", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-11-11T12:00:00Z"));
    setActivePinia(createTestingPinia());
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  const pumpForm = () =>
    controlForm("dhw", "dhwPump", ref({ dutypoint: stamp(0.5), on: stamp(true) }), [
      "dutypoint",
      "on",
    ]);

  it("sends the edited fields stamped as the component's control values, then refreshes", async () => {
    const history = useThrsHistory();
    vi.mocked(history.mutate).mockResolvedValue({} as never);
    const form = pumpForm();

    form.dutypoint.value.value = 0.8;
    await form.submit();

    const [query, variables] = vi.mocked(history.mutate).mock.lastCall as [DocumentNode, unknown];
    expect(print(query)).toContain("mutation ($input: ThrsControlDhwControlValuesInput!)");
    expect(print(query)).toContain("controlValues(input: $input)");
    expect(variables).toEqual({
      input: { dhwPump: { dutypoint: { value: 0.8, timeStamp: "2026-11-11T12:00:00.000Z" } } },
    });
    expect(history.refresh).toHaveBeenCalledOnce();
    expect(form.dutypoint.isDirty.value).toBe(false);
  });

  it("keeps the edits and shows why sending failed", async () => {
    const history = useThrsHistory();
    vi.mocked(history.mutate).mockResolvedValue({ error: { message: "Out of range" } } as never);
    const form = pumpForm();

    form.dutypoint.value.value = 2;
    await form.submit();

    expect(form.error.value).toBe("Out of range");
    expect(form.dutypoint.isDirty.value).toBe(true);
    expect(form.isSubmitting.value).toBe(false);
  });
});

describe("simulation inputs form", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-11-11T12:00:00Z"));
    setActivePinia(createTestingPinia());
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("sends the edited fields stamped as the component's simulation inputs", async () => {
    const simulation = useSimulationStore();
    vi.mocked(simulation.setInputs).mockResolvedValue({} as never);
    const form = simulationInputsForm(
      "thrustersSeawaterSupply",
      ref({ temperature: stamp(20), flow: stamp(3) }),
      ["temperature", "flow"],
    );

    form.flow.value.value = 4;
    await form.submit();

    expect(simulation.setInputs).toHaveBeenCalledWith({
      thrustersSeawaterSupply: { flow: { value: 4, timeStamp: "2026-11-11T12:00:00.000Z" } },
    });
    expect(form.flow.isDirty.value).toBe(false);
  });
});
