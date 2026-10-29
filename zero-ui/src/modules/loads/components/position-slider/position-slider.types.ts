import { Ref } from "vue";

export type SliderType = "symmetric" | "asymmetric";

export type PositionSliderTrackContext = {
  type: Ref<SliderType>;
};
