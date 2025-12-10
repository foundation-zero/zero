import { createContext } from "reka-ui";
import { Ref } from "vue";

export { default as PositionSlider } from "./PositionSlider.vue";
export { default as PositionSliderThumb } from "./PositionSliderThumb.vue";
export { default as PositionSliderTrack } from "./PositionSliderTrack.vue";

export type SliderType = "symmetric" | "asymmetric";

export type PositionSliderTrackContext = {
  type: Ref<SliderType>;
};

export const [getTrackContext, provideTrackContext] =
  createContext<PositionSliderTrackContext>("position-slider");
