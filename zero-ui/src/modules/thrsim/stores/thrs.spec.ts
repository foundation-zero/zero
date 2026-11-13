import { useThrsHistory } from "@/modules/thrapp/stores/history";
import { createTestingPinia } from "@pinia/testing";
import { DocumentNode, print } from "graphql";
import { setActivePinia } from "pinia";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ref } from "vue";
import { controlForm } from "./thrs";

vi.mock("@/modules/thrapp/graphql/client", () => ({
  mqttGraphqlClient: { query: vi.fn(), mutation: vi.fn() },
  mqttGraphqlContext: {},
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
