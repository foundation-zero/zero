import type { VariantProps } from "class-variance-authority";
import { cva } from "class-variance-authority";

export { default as Badge } from "./Badge.vue";

export const badgeVariants = cva(
  "inline-flex items-center justify-center rounded-md border text-xs font-medium w-fit whitespace-nowrap shrink-0 [&>svg]:size-3 gap-1 [&>svg]:pointer-events-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive transition-[color,box-shadow] overflow-hidden",
  {
    variants: {
      variant: {
        default: "border-transparent bg-inverse text-inverse-foreground [a&]:hover:bg-inverse/90",
        secondary:
          "border-transparent bg-border-subtle text-foreground [a&]:hover:bg-border-subtle/90",
        brand: "border-transparent bg-brand text-inverse-foreground [a&]:hover:bg-brand/90",
        constructive:
          "border-transparent bg-constructive text-inverse-foreground [a&]:hover:bg-constructive/90",
        warning: "border-transparent bg-warning text-inverse-foreground [a&]:hover:bg-warning/90",
        destructive:
          "border-transparent bg-destructive text-white [a&]:hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:focus-visible:ring-destructive/40 dark:bg-destructive/60",
        outline: "text-foreground [a&]:hover:bg-accent [a&]:hover:text-accent-foreground",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

export const badgeTypes = cva("", {
  variants: {
    variant: {
      default: "px-2 py-1",
      number: "px-1 py-0 rounded-full",
    },
  },
  defaultVariants: {
    variant: "default",
  },
});
export type BadgeVariants = VariantProps<typeof badgeVariants>;
export type BadgeTypes = VariantProps<typeof badgeTypes>;
