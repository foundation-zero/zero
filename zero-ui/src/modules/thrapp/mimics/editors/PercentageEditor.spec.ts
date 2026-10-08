import { mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ref } from "vue";
import PercentageEditor from "./PercentageEditor.vue";

const value = ref<number | undefined>();

vi.mock("@/modules/thrapp/mimics/providers", () => ({
  getFieldValue: () => value,
}));

vi.mock("@/modules/thrapp/mimics/editors", () => ({
  FieldEditor: {
    Number: {
      name: "NumberEditorStub",
      props: ["modelValue", "min", "max", "step", "formatOptions"],
      emits: ["update:modelValue"],
      template: "<div><slot /></div>",
    },
  },
}));

describe("percentage editing for flow ratios", () => {
  beforeEach(() => {
    value.value = undefined;
  });

  it.each([
    { ratio: 0, percentage: 0 },
    { ratio: 0.3, percentage: 30 },
    { ratio: 1, percentage: 100 },
  ])("displays $ratio as $percentage percent", ({ ratio, percentage }) => {
    value.value = ratio;
    const wrapper = mount(PercentageEditor);

    expect(wrapper.findComponent({ name: "NumberEditorStub" }).props("modelValue")).toBe(
      percentage,
    );
  });

  it("stores the edited percentage as a ratio", async () => {
    value.value = 0.3;
    const wrapper = mount(PercentageEditor);

    wrapper.findComponent({ name: "NumberEditorStub" }).vm.$emit("update:modelValue", 45);
    await wrapper.vm.$nextTick();

    expect(value.value).toBe(0.45);
  });

  it("uses percentage limits rather than flow-rate units", () => {
    const wrapper = mount(PercentageEditor);
    const editor = wrapper.findComponent({ name: "NumberEditorStub" });

    expect(editor.props("min")).toBe(0);
    expect(editor.props("max")).toBe(100);
    expect(editor.props("step")).toBe(1);
    expect(editor.props("formatOptions")).toEqual({ unit: "percent", style: "unit" });
  });
});
