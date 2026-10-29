import { Coords } from "./loads-gauge.types";

export const TICK_RADIUS = 22;
export const TICK_LENGTH = 5;
export const TICK_OFFSET = 10;
export const GAUGE_WIDTH = 320;
export const GAUGE_PADDING = 18;
export const GAUGE_HEIGHT = GAUGE_WIDTH / 2 + GAUGE_PADDING;
export const GAUGE_CENTER: Coords = { x: GAUGE_WIDTH / 2, y: GAUGE_HEIGHT };

export const GAUGE_RADIUS = 124;
export const POINT_ARC_RADIUS = 136;
export const POINT_RADIUS = 4;
export const START_ANGLE = 180;
export const END_ANGLE = 360;
export const TOTAL_ANGLE = (END_ANGLE - START_ANGLE + 360) % 360;
export const AMOUNT_OF_POINTS_PER_SIDE = 13;
export const TOTAL_AMOUNT_OF_POINTS = AMOUNT_OF_POINTS_PER_SIDE * 2 + 1;
export const ANGLE_STEP = TOTAL_ANGLE / (AMOUNT_OF_POINTS_PER_SIDE * 2);
export const EXTRA_TICK_THRESHOLD = AMOUNT_OF_POINTS_PER_SIDE * 0.5;
export const ARC_START_ANGLE = 166;
export const ARC_END_ANGLE = 14;

export const enum Colors {
  Transparent = "var(--color-muted/0)",
  Empty = "var(--color-muted)",
  Warning = "var(--color-warning)",
  Target = "var(--color-constructive)",
  Destructive = "var(--color-destructive)",
}
