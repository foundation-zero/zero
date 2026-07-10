import { ComponentOrientation } from "..";

export const FIGMA_URL =
  "https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=6147-48182&t=JfBIEDjiEP5NKk6I-4";

/** Square canvas - original geometry is 24x30; padded to 32x32 to prevent clipping on 90 degree rotation. */
export const LEVEL_SENSOR_WIDTH = 32;
export const LEVEL_SENSOR_HEIGHT = 32;
export const LEVEL_SENSOR_BASE_ORIENTATION = ComponentOrientation.Down;

export const LEVEL_SENSOR_BODY_FILL = "var(--background-muted)";
export const LEVEL_SENSOR_STROKE_COLOR = "var(--attention)";
export const LEVEL_SENSOR_MARK_COLOR = "var(--foreground)";
