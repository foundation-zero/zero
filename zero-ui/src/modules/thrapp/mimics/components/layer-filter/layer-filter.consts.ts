import { LayerFilterOption } from "./layer-filter.provider";

/** Every filter option, in the order they are shown. */
export const LAYER_FILTER_OPTIONS = [
  LayerFilterOption.SensorValues,
  LayerFilterOption.Flows,
  LayerFilterOption.YardTags,
  LayerFilterOption.Bypasses,
  LayerFilterOption.SupportComponents,
  LayerFilterOption.ManualComponents,
  LayerFilterOption.DirectionArrows,
] as const;
