export { default as IndicatorLight } from "./IndicatorLight.vue";

import type { VariantProps } from "class-variance-authority";
import { cva } from "class-variance-authority";

export const indicatorLightVariants = cva("size-full rounded-full", {
  variants: {
    variant: {
      default: "default",
      constructive: "constructive",
      destructive: "destructive",
    },
  },
  defaultVariants: {
    variant: "default",
  },
});

export type IndicatorLightVariants = VariantProps<typeof indicatorLightVariants>;
