import i18n from "@/i18n";
import { mount } from "@vue/test-utils";
import { describe, expect, it } from "vitest";
import { createLayerFilterContext, LayerFilterOption } from "./layer-filter.provider";
import LayerFilterOptions from "./LayerFilterOptions.vue";

const ALL_OPTIONS = [
  LayerFilterOption.ManualComponents,
  LayerFilterOption.Bypasses,
  LayerFilterOption.SupportComponents,
  LayerFilterOption.Flows,
  LayerFilterOption.DirectionArrows,
];

const mountOptions = (options: LayerFilterOption[]) => {
  const context = createLayerFilterContext();
  const wrapper = mount(LayerFilterOptions, {
    props: { options },
    global: { plugins: [i18n], provide: { layerFilterContext: context } },
  });
  return { context, wrapper };
};

describe("LayerFilterOptions", () => {
  it("labels every option from the translations, in the given order", () => {
    const { wrapper } = mountOptions(ALL_OPTIONS);

    expect(wrapper.findAll("label").map((label) => label.text())).toEqual([
      "Manual components",
      "Bypasses",
      "Support components",
      "Flows",
      "Direction arrows",
    ]);
  });

  it("activates every filter by default", () => {
    const { wrapper } = mountOptions(ALL_OPTIONS);

    expect(wrapper.findAll("[role=switch]").map((item) => item.attributes("data-state"))).toEqual(
      ALL_OPTIONS.map(() => "checked"),
    );
  });

  it("toggles a filter", async () => {
    const { context, wrapper } = mountOptions([LayerFilterOption.Bypasses]);

    await wrapper.get("[role=switch]").trigger("click");

    expect(context.isFilterActive(LayerFilterOption.Bypasses)).toBe(false);
  });
});
