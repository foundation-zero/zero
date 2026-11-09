import { mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it } from "vitest";
import { defineComponent, h, nextTick } from "vue";
import { createLayerFilterContext, LayerFilterOption } from "../layer-filter/layer-filter.provider";
import Label from "./Label.vue";
import { LabelTarget } from "./label.types";
import { provideLabelTarget } from "./label.utils";

const TARGET: LabelTarget = { x: 100, y: 100, width: 32, height: 32 };

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

  const visible = wrapper.get("hgroup:not([aria-hidden])");

  return {
    label: wrapper.get("svg").isVisible(),
    tag: visible.get("header").isVisible(),
    value: visible.find("p").exists() && visible.get("p").isVisible(),
  };
};

/** Mounts a label next to the target component, as the instances render it. */
const mountPlaced = (props: Record<string, unknown>, target: LabelTarget | null = TARGET) => {
  const Instance = defineComponent(() => {
    const labelTarget = provideLabelTarget();
    labelTarget.value = target ?? undefined;

    return () => h(Label, props, { default: () => "1038-45", value: () => "68 °C" });
  });

  return mount(Instance, {
    global: { provide: { layerFilterContext: createLayerFilterContext() } },
  });
};

const alignmentOf = (wrapper: ReturnType<typeof mountPlaced>) =>
  wrapper
    .get("hgroup:not([aria-hidden])")
    .classes()
    .filter((name) => name.startsWith("self-") || name.startsWith("justify-self-"));

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

  it("keeps both rows in the invisible copy of the label", async () => {
    const context = createLayerFilterContext();
    context.setFilter(LayerFilterOption.YardTags, false);
    const wrapper = mount(Label, {
      slots: { default: "1038-45", value: "68 °C" },
      global: { provide: { layerFilterContext: context } },
      attachTo: document.body,
    });
    await nextTick();
    const placeholder = wrapper.get("hgroup[aria-hidden]");

    expect(placeholder.classes()).toContain("invisible");
    expect(placeholder.get("header").attributes("style")).toBeUndefined();
    expect(placeholder.get("p").attributes("style")).toBeUndefined();
    expect(wrapper.get("hgroup:not([aria-hidden]) header").isVisible()).toBe(false);
  });

  it.each([
    { placement: "above", props: { x: 90, y: 60 }, alignment: ["self-end"] },
    { placement: "below", props: { x: 90, y: 140 }, alignment: ["self-start"] },
    {
      placement: "start",
      props: { x: 40, y: 100 },
      alignment: ["self-center", "justify-self-end"],
    },
    {
      placement: "end",
      props: { x: 140, y: 100 },
      alignment: ["self-center", "justify-self-start"],
    },
  ])("aligns a label $placement its component towards it", ({ props, alignment }) => {
    expect(alignmentOf(mountPlaced(props))).toEqual(alignment);
  });

  it("centres a label centred above its component", () => {
    const wrapper = mountPlaced({ targetX: 100, targetWidth: 32, y: 60 });

    expect(alignmentOf(wrapper)).toEqual(["self-end", "justify-self-center"]);
  });

  it("aligns a label centred beside its component towards it", () => {
    const wrapper = mountPlaced({ targetX: 100, targetWidth: -32, y: 100 });

    expect(alignmentOf(wrapper)).toEqual(["self-center", "justify-self-end"]);
  });

  it("keeps the top of a label without a component in place", () => {
    expect(alignmentOf(mountPlaced({ x: 90, y: 60 }, null))).toEqual(["self-start"]);
  });
});
