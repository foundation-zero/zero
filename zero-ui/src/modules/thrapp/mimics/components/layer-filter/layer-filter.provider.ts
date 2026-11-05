import { computed, inject, provide, ref, Ref } from "vue";

export const enum LayerFilterOption {
  ManualComponents = "ManualComponent",
  Bypasses = "Bypasses",
  Flows = "Flows",
  Pipes = "Pipes",
  DirectionArrows = "DirectionArrows",
}

export interface LayerFilterContext {
  activeFilters: Ref<Record<LayerFilterOption, boolean>>;
  toggleFilter: (option: LayerFilterOption) => void;
  setFilter: (option: LayerFilterOption, value: boolean) => void;
  getFilter: (option: LayerFilterOption) => Ref<boolean>;
  isFilterActive: (option: LayerFilterOption) => boolean;
}

export const createLayerFilterContext = (): LayerFilterContext => {
  const activeFilters: Ref<Record<LayerFilterOption, boolean>> = ref({
    [LayerFilterOption.ManualComponents]: false,
    [LayerFilterOption.Bypasses]: false,
    [LayerFilterOption.Flows]: true,
    [LayerFilterOption.Pipes]: true,
    [LayerFilterOption.DirectionArrows]: false,
  });

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
