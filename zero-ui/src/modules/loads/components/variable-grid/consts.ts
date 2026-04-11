import { BreakpointsZero } from "@/modules/common/lib/consts";

export type GridBreakpoints = keyof BreakpointsZero | "";

export const NUMERIC_GRID_SIZE: Record<GridBreakpoints, number> = {
  "": 2,
  sm: 3,
  md: 4,
  lg: 6,
  xl: 8,
  "2xl": 10,
  "3xl": 12,
  "4xl": 14,
};

export const GAUGE_GRID_SIZE: Record<GridBreakpoints, number> = {
  "": 1,
  sm: 1,
  md: 2,
  lg: 3,
  xl: 4,
  "2xl": 5,
  "3xl": 6,
  "4xl": 7,
};
