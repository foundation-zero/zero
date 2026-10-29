import { cva } from "class-variance-authority";

export const indicatorLightVariants = cva("size-full rounded-full", {
  variants: {
    variant: {
      neutral: "neutral",
      constructive: "constructive",
      destructive: "destructive",
    },
  },
  defaultVariants: {
    variant: "neutral",
  },
});
