import { Ratio } from "@/modules/thrapp/types/thrs";
import { SolarPanelOrientation, SolarPanelSize } from "./solar-panel.consts";

export type SolarPanelProps = {
  size?: SolarPanelSize;
  orientation?: SolarPanelOrientation;
  /** Relative yield (0..1); undefined renders the panel without a yield fill. */
  yieldRatio?: Ratio;
};
