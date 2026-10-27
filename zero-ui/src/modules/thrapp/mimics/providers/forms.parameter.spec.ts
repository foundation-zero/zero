import { ParametersType } from "@/modules/thrsim/types";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ref } from "vue";
import { ModuleField } from ".";
import { createParameterFormContext } from "./forms.parameter";

const parameter = ref<number | undefined>();
const setParameter = vi.fn();
const automaticMode = ref<boolean | undefined>(true);
const advisoryEnabled = ref<boolean | null>(true);

vi.mock(".", async (importOriginal) => ({
  ...(await importOriginal()),
  getMimicDataProvider: () => ({
    getParameter: () => parameter,
    setParameter,
  }),
}));

vi.mock("../../state", () => ({
  useAutomaticMode: () => automaticMode,
  useAdvisoryEnabled: () => advisoryEnabled,
}));

vi.mock(import("vue-router"), async (importOriginal) => ({
  ...(await importOriginal()),
  useRoute: vi.fn(() => ({ query: {} }) as ReturnType<(typeof import("vue-router"))["useRoute"]>),
}));

const source: ModuleField<ParametersType.Temperature> = [
  ParametersType.Temperature,
  "thrusters",
  "minimumTemperature",
  null,
];

describe("parameter value form", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    parameter.value = 60;
    automaticMode.value = true;
    advisoryEnabled.value = true;
    setParameter.mockReset().mockResolvedValue(undefined);
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("shows the edited value right away and submits only the last edit after a pause", async () => {
    const form = createParameterFormContext(source);

    form.update(65);
    form.update(70);
    expect(form.value.value).toBe(70);
    expect(setParameter).not.toHaveBeenCalled();

    await vi.advanceTimersByTimeAsync(1000);

    expect(setParameter).toHaveBeenCalledExactlyOnceWith(source, 70);
    expect(form.isDirty.value).toBe(false);
  });

  it("is only editable in automatic mode", async () => {
    automaticMode.value = false;
    const form = createParameterFormContext(source);

    form.update(70);
    await vi.advanceTimersByTimeAsync(1000);

    expect(form.isEditable.value).toBe(false);
    expect(setParameter).not.toHaveBeenCalled();
  });

  it("exposes the error message when submitting fails", async () => {
    setParameter.mockRejectedValue(new Error("Out of range"));
    const form = createParameterFormContext(source);

    form.update(70);
    await vi.advanceTimersByTimeAsync(1000);

    expect(form.error.value).toBe("Out of range");
    expect(form.value.value).toBe(60);
  });
});
