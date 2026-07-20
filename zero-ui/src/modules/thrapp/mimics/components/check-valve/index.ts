import { ComponentOrientation } from "..";

export const FIGMA_URL =
  "https://www.figma.com/design/DDNAUHsV56fQMTh3Ej76gL/App-screens---On-board-monitoring?node-id=6147-45042&t=JfBIEDjiEP5NKk6I-4";

/** Square canvas — original geometry is 24×32; padded to 32×32 to prevent clipping on 90° rotation. */
export const CHECK_VALVE_WIDTH = 32;
export const CHECK_VALVE_HEIGHT = 32;
export const CHECK_VALVE_BASE_ORIENTATION = ComponentOrientation.Right;

export const CHECK_VALVE_BODY_FILL = "var(--muted)";
export const CHECK_VALVE_STROKE_COLOR = "var(--brand-muted)";
export const CHECK_VALVE_MARK_COLOR = "var(--foreground)";
