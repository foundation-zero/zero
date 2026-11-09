import { mount } from "@vue/test-utils";
import { beforeEach, describe, expect, it } from "vitest";
import { h, nextTick } from "vue";
import { LAYER_FILTER_OPTIONS } from "./layer-filter.consts";
import {
  createLayerFilterContext,
  LayerFilterContext,
  LayerFilterOption,
  provideLayerFilterContext,
  useLayerFilterContext,
} from "./layer-filter.provider";

const STORAGE_KEY = "layerFilterContext";

describe("createLayerFilterContext", () => {
  beforeEach(() => localStorage.clear());

  it("activates every filter by default", () => {
    const { isFilterActive } = createLayerFilterContext();

    expect(LAYER_FILTER_OPTIONS.map(isFilterActive)).toEqual(LAYER_FILTER_OPTIONS.map(() => true));
  });

  it("toggles a filter off and on again", () => {
    const { isFilterActive, toggleFilter } = createLayerFilterContext();

    toggleFilter(LayerFilterOption.Flows);
    expect(isFilterActive(LayerFilterOption.Flows)).toBe(false);

    toggleFilter(LayerFilterOption.Flows);
    expect(isFilterActive(LayerFilterOption.Flows)).toBe(true);
  });

  it("sets a filter without touching the others", () => {
    const { isFilterActive, setFilter } = createLayerFilterContext();

    setFilter(LayerFilterOption.Bypasses, false);

    expect(isFilterActive(LayerFilterOption.Bypasses)).toBe(false);
    expect(isFilterActive(LayerFilterOption.Flows)).toBe(true);
  });

  it("exposes a filter as a ref that follows changes", () => {
    const { getFilter, setFilter } = createLayerFilterContext();
    const filter = getFilter(LayerFilterOption.YardTags);

    setFilter(LayerFilterOption.YardTags, false);

    expect(filter.value).toBe(false);
  });

  it("sets a filter through its ref", () => {
    const { getFilter, isFilterActive } = createLayerFilterContext();

    getFilter(LayerFilterOption.SensorValues).value = false;

    expect(isFilterActive(LayerFilterOption.SensorValues)).toBe(false);
  });

  it("stores the selection", async () => {
    const { setFilter } = createLayerFilterContext();

    setFilter(LayerFilterOption.Bypasses, false);
    await nextTick();

    expect(JSON.parse(localStorage.getItem(STORAGE_KEY) ?? "{}")).toMatchObject({
      [LayerFilterOption.Bypasses]: false,
    });
  });

  it("restores a stored selection", () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ [LayerFilterOption.Bypasses]: false }));

    const { isFilterActive } = createLayerFilterContext();

    expect(isFilterActive(LayerFilterOption.Bypasses)).toBe(false);
  });

  it("defaults options missing from a stored selection", () => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ [LayerFilterOption.Bypasses]: false }));

    const { isFilterActive } = createLayerFilterContext();

    expect(isFilterActive(LayerFilterOption.YardTags)).toBe(true);
  });
});

describe("useLayerFilterContext", () => {
  let injected: LayerFilterContext | undefined;

  const Consumer = {
    setup() {
      injected = useLayerFilterContext();
      return () => h("div");
    },
  };

  beforeEach(() => {
    localStorage.clear();
    injected = undefined;
  });

  it("returns the provided context", () => {
    const context = createLayerFilterContext();
    const Provider = {
      setup() {
        provideLayerFilterContext(context);
        return () => h(Consumer);
      },
    };

    mount(Provider);

    expect(injected).toBe(context);
  });

  it("throws without a provider", () => {
    expect(() => mount(Consumer)).toThrow("LayerFilterContext not provided");
  });
});
