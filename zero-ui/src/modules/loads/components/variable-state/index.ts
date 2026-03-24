export { default as VariableState } from "./VariableState.vue";
export { default as VariableUnit } from "./VariableUnit.vue";

import type { VariantProps } from "class-variance-authority";
import { cva } from "class-variance-authority";

export const variableStateVariants = cva("relative inline-flex justify-center transition-colors", {
  variants: {
    state: {
      unknown: "text-disabled-foreground",
      neutral: "text-foreground",
      alarm: "text-destructive",
      warning: "text-warning",
    },
    size: {
      xl: "font-semibold text-5xl [&>[data-slot='load-value']]:font-headers items-baseline leading-[4rem]",
      lg: "font-medium text-xl",
      sm: "font-medium text-sm",
    },
  },
  defaultVariants: {
    state: "unknown",
    size: "lg",
  },
});

export type VariableStateVariants = VariantProps<typeof variableStateVariants>;
