import i18n from "@/i18n";
import { SensorComponentType } from "@/modules/thrapp/types/thrs";
import { mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { h, nextTick, SetupContext } from "vue";
import {
  createLayerFilterContext,
  LayerFilterOption,
} from "../components/layer-filter/layer-filter.provider";
import { ModuleField } from "../providers";
import PortTemperatureLabelInstance from "./PortTemperatureLabelInstance.vue";

vi.mock("../providers", () => ({
  SensorValue: {
    setup:
      (_: unknown, { slots }: SetupContext) =>
      () =>
        slots.default?.(),
  },
}));
vi.mock("../renderers", () => ({
  FieldRenderer: { Temperature: { setup: () => () => h("i", "20 °C") } },
}));

const mountLabel = async ({ yardTags = true, sensorValues = true }) => {
  const context = createLayerFilterContext();
  context.setFilter(LayerFilterOption.YardTags, yardTags);
  context.setFilter(LayerFilterOption.SensorValues, sensorValues);

  const wrapper = mount(PortTemperatureLabelInstance, {
    props: {
      temperature: [] as unknown as ModuleField<SensorComponentType.HeatTransferDevice>,
      field: "temperatureIn" as never,
      port: "in",
    },
    global: { plugins: [i18n], provide: { layerFilterContext: context } },
    attachTo: document.body,
  });
  await nextTick();

  return {
    label: wrapper.get("foreignObject").isVisible(),
    tag: wrapper.get(".text-brand").isVisible(),
    value: wrapper.get(".text-muted-foreground").isVisible(),
  };
};

describe("PortTemperatureLabelInstance", () => {
  beforeEach(() => localStorage.clear());

  it("shows the port and temperature when both filters are active", async () => {
    expect(await mountLabel({})).toEqual({ label: true, tag: true, value: true });
  });

  it("only shows the temperature without yard tags", async () => {
    expect(await mountLabel({ yardTags: false })).toEqual({
      label: true,
      tag: false,
      value: true,
    });
  });

  it("only shows the port without sensor values", async () => {
    expect(await mountLabel({ sensorValues: false })).toEqual({
      label: true,
      tag: true,
      value: false,
    });
  });

  it("hides entirely without both", async () => {
    const { label } = await mountLabel({ yardTags: false, sensorValues: false });

    expect(label).toBe(false);
  });
});
