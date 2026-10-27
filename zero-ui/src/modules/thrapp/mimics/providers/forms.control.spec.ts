import { ControlComponentType, ControlDefinitionMap } from "@/modules/thrapp/types/thrs";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ref } from "vue";
import { ModuleField } from ".";
import { createFormContext } from "./forms.control";

const control = ref<ControlDefinitionMap[ControlComponentType.Pump] | undefined>();
const setControlValue = vi.fn();
const automaticMode = ref<boolean | undefined>(false);
const advisoryEnabled = ref<boolean | null>(true);

vi.mock(".", async (importOriginal) => ({
  ...(await importOriginal()),
  getMimicDataProvider: () => ({
    getControlValue: () => control,
    setControlValue,
  }),
}));

vi.mock("../../state", () => ({
  useAutomaticMode: () => automaticMode,
  useAdvisoryEnabled: () => advisoryEnabled,
}));

const stamp = <T>(value: T) => ({ value, timestamp: new Date() });
const source: ModuleField<ControlComponentType.Pump> = [
  ControlComponentType.Pump,
  "thrusters",
  "pump",
  null,
];

describe("control value form", () => {
  beforeEach(() => {
    control.value = { dutypoint: stamp(0.5), on: stamp(true) };
    automaticMode.value = false;
    advisoryEnabled.value = true;
    setControlValue.mockReset().mockResolvedValue(undefined);
  });

  it.each([
    { automatic: false, advisory: true, editable: true },
    { automatic: true, advisory: true, editable: false },
    { automatic: false, advisory: false, editable: false },
  ])(
    "is editable=$editable when automatic=$automatic and advisory=$advisory",
    ({ automatic, advisory, editable }) => {
      automaticMode.value = automatic;
      advisoryEnabled.value = advisory;

      expect(createFormContext(source).isEditable.value).toBe(editable);
    },
  );

  it("shows edits over the live value until they are undone", () => {
    const form = createFormContext(source);
    const dutypoint = form.getValue("dutypoint");

    form.update("dutypoint", 0.8);
    expect(dutypoint.value).toBe(0.8);
    expect(form.isDirty.value).toBe(true);

    form.undo();
    expect(dutypoint.value).toBe(0.5);
    expect(form.isDirty.value).toBe(false);
  });

  it("submits the live values merged with the edits and clears the edits", async () => {
    const form = createFormContext(source);

    form.update("dutypoint", 0.8);
    await form.submit();

    expect(setControlValue).toHaveBeenCalledWith(source, { dutypoint: 0.8, on: true });
    expect(form.isDirty.value).toBe(false);
    expect(form.isPending.value).toBe(false);
  });

  it("does not submit in automatic mode", async () => {
    automaticMode.value = true;
    const form = createFormContext(source);

    form.update("dutypoint", 0.8);
    await form.submit();

    expect(setControlValue).not.toHaveBeenCalled();
  });

  it("exposes the error message when submitting fails", async () => {
    setControlValue.mockRejectedValue(new Error("PLC unreachable"));
    const form = createFormContext(source);

    form.update("dutypoint", 0.8);
    await form.submit();

    expect(form.error.value).toBe("PLC unreachable");
    expect(form.isPending.value).toBe(false);
  });
});
