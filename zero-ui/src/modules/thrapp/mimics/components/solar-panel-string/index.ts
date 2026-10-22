import { Ratio } from "@/modules/thrsim/types";
import { SolarPanelOrientation, SolarPanelSize } from "../solar-panel";

export { default as SolarPanelString } from "./SolarPanelString.vue";

export type SolarPanelPlacement = {
  x: number;
  y: number;
  size?: SolarPanelSize;
  orientation?: SolarPanelOrientation;
};

/** A rectangular frame, or an arbitrary outline path for strings that are not rectangular. */
export type SolarPanelStringFrame =
  | { x: number; y: number; width: number; height: number }
  | { d: string };

export type SolarPanelStringLabel = {
  /** Centre of the label. */
  x: number;
  y: number;
  vertical?: boolean;
};

export type SolarPanelStringProps = {
  frame: SolarPanelStringFrame;
  panels: SolarPanelPlacement[];
  label?: SolarPanelStringLabel;
  /** Relative yield (0..1) of the string, applied to all of its panels. */
  yieldRatio?: Ratio;
};
