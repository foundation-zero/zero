import { Ratio } from "@/modules/thrapp/types/thrs";
import { YIELD_STEPS } from "./solar-panel.consts";

/** Maps a relative yield to the amber scale: dark for a low yield, light for a high yield. */
export const solarYieldColor = (yieldRatio: Ratio) =>
  `var(--color-accent-b-${YIELD_STEPS[Math.round(Math.min(Math.max(yieldRatio, 0), 1) * 10)]})`;
