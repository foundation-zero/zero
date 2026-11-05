import i18n from "@/i18n";
import { mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it } from "vitest";
import { LAYER_FILTER_OPTIONS } from "./layer-filter.consts";
import { createLayerFilterContext, LayerFilterOption } from "./layer-filter.provider";
import LayerFilterOptions from "./LayerFilterOptions.vue";

const mountOptions = (options: LayerFilterOption[]) => {
  const context = createLayerFilterContext();
  const wrapper = mount(LayerFilterOptions, {
    props: { options },
    global: { plugins: [i18n], provide: { layerFilterContext: context } },
  });
  return { context, wrapper };
};

describe("LayerFilterOptions", () => {
  beforeEach(() => localStorage.clear());

  it("labels every option from the translations, in the fixed order", () => {
    const { wrapper } = mountOptions([...LAYER_FILTER_OPTIONS]);

    expect(wrapper.findAll("label").map((label) => label.text())).toEqual([
      "Sensor values",
      "Flows",
      "Yard tags",
      "Bypasses",
      "Support components",
      "Manual components",
      "Direction arrows",
    ]);
  });

  it("activates every filter by default", () => {
    const { wrapper } = mountOptions([...LAYER_FILTER_OPTIONS]);

    expect(wrapper.findAll("[role=switch]").map((item) => item.attributes("data-state"))).toEqual(
      LAYER_FILTER_OPTIONS.map(() => "checked"),
    );
  });

  it("toggles a filter", async () => {
    const { context, wrapper } = mountOptions([LayerFilterOption.Bypasses]);

    await wrapper.get("[role=switch]").trigger("click");

    expect(context.isFilterActive(LayerFilterOption.Bypasses)).toBe(false);
  });
});
