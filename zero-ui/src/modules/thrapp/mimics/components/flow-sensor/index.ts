import { ComponentOrientation } from "..";

export const FIGMA_URL =
  "https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=6147-48175&t=JfBIEDjiEP5NKk6I-4";

/** Square canvas — original geometry is 24×40; padded to 40×40 to prevent clipping on 90° rotation. */
export const FLOW_SENSOR_WIDTH = 40;
export const FLOW_SENSOR_HEIGHT = 40;
export const FLOW_SENSOR_BASE_ORIENTATION = ComponentOrientation.Down;

export const FLOW_SENSOR_BODY_FILL = "var(--muted)";
export const FLOW_SENSOR_STROKE_COLOR = "var(--attention)";
export const FLOW_SENSOR_MARK_COLOR = "var(--foreground)";
