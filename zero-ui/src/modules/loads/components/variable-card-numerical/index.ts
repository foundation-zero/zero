export { default as VariableCardNumerical } from "./VariableCardNumerical.vue";

import { cva, VariantProps } from "class-variance-authority";

export const variableCardNumericalVariants = cva("", {
  variants: {
    type: {
      number: "text-foreground",
      percentage: "text-constructive",
    },
  },
  defaultVariants: {
    type: "number",
  },
});

export type VariableCardNumericalVariants = VariantProps<typeof variableCardNumericalVariants>;
