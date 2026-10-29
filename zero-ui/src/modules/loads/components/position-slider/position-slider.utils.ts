import { createContext } from "reka-ui";
import { PositionSliderTrackContext } from "./position-slider.types";

export const [getTrackContext, provideTrackContext] =
  createContext<PositionSliderTrackContext>("position-slider");
