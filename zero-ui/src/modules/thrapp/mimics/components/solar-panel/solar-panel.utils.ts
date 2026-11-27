import { Ratio } from "@/modules/thrapp/types/thrs";
import {
  SOLAR_PANEL_DIMENSIONS,
  SOLAR_PANEL_PEAK_HEAT,
  SolarPanelSize,
  YIELD_STEPS,
} from "./solar-panel.consts";

/** Peak heat of a panel in W; a small panel by its share of a large panel's area. */
export function solarPanelPeakHeat(size = SolarPanelSize.Large) {
  return (
    (SOLAR_PANEL_PEAK_HEAT * SOLAR_PANEL_DIMENSIONS[size].width) /
    SOLAR_PANEL_DIMENSIONS[SolarPanelSize.Large].width
  );
}

/** Maps a relative yield to the amber scale: dark for a low yield, light for a high yield. */
export const solarYieldColor = (yieldRatio: Ratio) =>
  `var(--color-accent-b-${YIELD_STEPS[Math.round(Math.min(Math.max(yieldRatio, 0), 1) * 10)]})`;
