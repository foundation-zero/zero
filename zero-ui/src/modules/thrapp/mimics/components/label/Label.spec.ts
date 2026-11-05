import { mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it } from "vitest";
import { nextTick } from "vue";
import { createLayerFilterContext, LayerFilterOption } from "../layer-filter/layer-filter.provider";
import Label from "./Label.vue";

const mountLabel = async ({
  value = true,
  yardTags = true,
  sensorValues = true,
  unfiltered = false,
}) => {
  const context = createLayerFilterContext();
  context.setFilter(LayerFilterOption.YardTags, yardTags);
  context.setFilter(LayerFilterOption.SensorValues, sensorValues);

  const wrapper = mount(Label, {
    props: { unfiltered },
    slots: { default: "1038-45", ...(value ? { value: "68 °C" } : {}) },
    global: { provide: { layerFilterContext: context } },
    attachTo: document.body,
  });
  await nextTick();

  return {
    label: wrapper.get("svg").isVisible(),
    tag: wrapper.get("header").isVisible(),
    value: wrapper.find("p").exists() && wrapper.get("p").isVisible(),
  };
};

describe("Label", () => {
  beforeEach(() => localStorage.clear());

  it("shows the tag and value when both filters are active", async () => {
    expect(await mountLabel({})).toEqual({ label: true, tag: true, value: true });
  });

  it("hides a tag-only label entirely without yard tags", async () => {
    const { label } = await mountLabel({ value: false, yardTags: false });

    expect(label).toBe(false);
  });

  it("keeps a tag-only label without sensor values", async () => {
    const { label, tag } = await mountLabel({ value: false, sensorValues: false });

    expect({ label, tag }).toEqual({ label: true, tag: true });
  });

  it("only hides the tag of a label with a value without yard tags", async () => {
    expect(await mountLabel({ yardTags: false })).toEqual({
      label: true,
      tag: false,
      value: true,
    });
  });

  it("only shows the tag of a label with a value without sensor values", async () => {
    expect(await mountLabel({ sensorValues: false })).toEqual({
      label: true,
      tag: true,
      value: false,
    });
  });

  it("hides a label with a value entirely without both", async () => {
    const { label } = await mountLabel({ yardTags: false, sensorValues: false });

    expect(label).toBe(false);
  });

  it("ignores the filters when unfiltered", async () => {
    expect(await mountLabel({ yardTags: false, sensorValues: false, unfiltered: true })).toEqual({
      label: true,
      tag: true,
      value: true,
    });
  });
});
