import { Ratio } from "@/modules/thrapp/types/thrs";

export { default as SolarPanel } from "./SolarPanel.vue";

export const FIGMA_URL =
  "https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=9138-285162";

export const enum SolarPanelSize {
  Large = "large",
  Small = "small",
}

export const enum SolarPanelOrientation {
  Portrait = "portrait",
  Landscape = "landscape",
}

/** Portrait dimensions; landscape panels swap width and height. */
export const SOLAR_PANEL_DIMENSIONS: Record<SolarPanelSize, { width: number; height: number }> = {
  [SolarPanelSize.Large]: { width: 27, height: 36 },
  [SolarPanelSize.Small]: { width: 14, height: 36 },
};

/** Cell grid of the portrait panel, as x positions of the columns and y positions of the rows. */
export const SOLAR_PANEL_GRID: Record<SolarPanelSize, { columns: number[]; rows: number[] }> = {
  [SolarPanelSize.Large]: {
    columns: [2.77, 5.77, 8.77, 11.77, 14.77, 17.77, 20.77, 23.77],
    rows: [2.9, 5.9, 8.9, 11.9, 14.9, 17.9, 20.9, 23.9, 26.9, 29.82, 32.75],
  },
  [SolarPanelSize.Small]: {
    columns: [2.33, 5.44, 8.56, 11.67],
    rows: [2.9, 5.9, 8.9, 11.9, 14.9, 17.9, 20.9, 23.9, 26.9, 29.82, 32.75],
  },
};

export type SolarPanelProps = {
  size?: SolarPanelSize;
  orientation?: SolarPanelOrientation;
  /** Relative yield (0..1); undefined renders the panel without a yield fill. */
  yieldRatio?: Ratio;
};

const YIELD_STEPS = [1000, 900, 800, 700, 600, 500, 400, 300, 200, 100, 0];

/** Maps a relative yield to the amber scale: dark for a low yield, light for a high yield. */
export const solarYieldColor = (yieldRatio: Ratio) =>
  `var(--color-accent-b-${YIELD_STEPS[Math.round(Math.min(Math.max(yieldRatio, 0), 1) * 10)]})`;
