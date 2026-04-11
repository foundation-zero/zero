import { breakpointsTailwind } from "@vueuse/core";

export type BreakpointsZero = typeof breakpointsTailwind & {
  "3xl": number;
  "4xl": number;
};

export const breakpointsZero: BreakpointsZero = {
  ...breakpointsTailwind,
  "3xl": 120 * 16,
  "4xl": 144 * 16,
};
