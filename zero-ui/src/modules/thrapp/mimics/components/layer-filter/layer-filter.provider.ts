import { useLocalStorage } from "@vueuse/core";
import { computed, inject, provide, Ref } from "vue";

export const enum LayerFilterOption {
  ManualComponents = "ManualComponent",
  Bypasses = "Bypasses",
  SupportComponents = "SupportComponents",
  Flows = "Flows",
  DirectionArrows = "DirectionArrows",
  YardTags = "YardTags",
  SensorValues = "SensorValues",
}

export interface LayerFilterContext {
  activeFilters: Ref<Record<LayerFilterOption, boolean>>;
  toggleFilter: (option: LayerFilterOption) => void;
  setFilter: (option: LayerFilterOption, value: boolean) => void;
  getFilter: (option: LayerFilterOption) => Ref<boolean>;
  isFilterActive: (option: LayerFilterOption) => boolean;
}

export const createLayerFilterContext = (): LayerFilterContext => {
  const activeFilters = useLocalStorage<Record<LayerFilterOption, boolean>>(
    "layerFilterContext",
    {
      [LayerFilterOption.ManualComponents]: true,
      [LayerFilterOption.Bypasses]: true,
      [LayerFilterOption.SupportComponents]: true,
      [LayerFilterOption.Flows]: true,
      [LayerFilterOption.DirectionArrows]: true,
      [LayerFilterOption.YardTags]: true,
      [LayerFilterOption.SensorValues]: true,
    },
    // Selections stored before an option existed still need its default.
    { mergeDefaults: true },
  );

  const toggleFilter = (option: LayerFilterOption) => {
    activeFilters.value[option] = !activeFilters.value[option];
    activeFilters.value = { ...activeFilters.value };
  };

  const setFilter = (option: LayerFilterOption, value: boolean) => {
    activeFilters.value[option] = value;
    activeFilters.value = { ...activeFilters.value };
  };

  const isFilterActive = (option: LayerFilterOption) => {
    return activeFilters.value[option];
  };

  const getFilter = (option: LayerFilterOption) => {
    return computed({
      get() {
        return activeFilters.value[option];
      },
      set(value: boolean) {
        setFilter(option, value);
      },
    });
  };

  return {
    activeFilters,
    toggleFilter,
    setFilter,
    getFilter,
    isFilterActive,
  };
};

export const provideLayerFilterContext = (context: LayerFilterContext) =>
  provide("layerFilterContext", context);

export const useLayerFilterContext = (): LayerFilterContext => {
  const context = inject<LayerFilterContext>("layerFilterContext");
  if (!context) {
    throw new Error("LayerFilterContext not provided");
  }
  return context;
};
