export { default as VariableState } from "./VariableState.vue";
export { default as VariableUnit } from "./VariableUnit.vue";

import type { VariantProps } from "class-variance-authority";
import { cva } from "class-variance-authority";

export const variableStateVariants = cva("relative flex justify-center", {
  variants: {
    state: {
      unknown: "text-disabled-foreground",
      neutral: "text-foreground",
      alarm: "text-destructive",
      warning: "text-warning",
    },
    size: {
      xl: "font-semibold text-6xl [&>[data-slot='load-value']]:font-headers",
      lg: "font-medium text-xl",
    },
  },
  defaultVariants: {
    state: "unknown",
    size: "lg",
  },
});

export type VariableStateVariants = VariantProps<typeof variableStateVariants>;
