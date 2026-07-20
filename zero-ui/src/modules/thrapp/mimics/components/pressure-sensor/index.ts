import { ComponentOrientation } from "..";

export const FIGMA_URL =
  "https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=6147-48179&t=JfBIEDjiEP5NKk6I-4";

/** Square canvas — original geometry is 24×30; padded to 32×32 to prevent clipping on 90° rotation. */
export const PRESSURE_SENSOR_WIDTH = 32;
export const PRESSURE_SENSOR_HEIGHT = 32;
export const PRESSURE_SENSOR_BASE_ORIENTATION = ComponentOrientation.Down;

export const PRESSURE_SENSOR_BODY_FILL = "var(--muted)";
export const PRESSURE_SENSOR_STROKE_COLOR = "var(--attention)";
export const PRESSURE_SENSOR_MARK_COLOR = "var(--foreground)";
