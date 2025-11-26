import { cva, type VariantProps } from "class-variance-authority";

export { default as Button } from "./Button.vue";

export const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 cursor-pointer whitespace-nowrap rounded-md text-sm font-medium transition-all disabled:pointer-events-none [&_svg]:pointer-events-none [&_svg:not([class*='size-'])]:size-4 shrink-0 [&_svg]:shrink-0 outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px] aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive duration-250",
  {
    variants: {
      variant: {
        default:
          "bg-inverse text-inverse-foreground shadow-xs hover:bg-inverse-muted active:bg-brand disabled:bg-disabled disabled:text-disabled-foreground",
        secondary:
          "bg-muted border-border-subtle border text-muted-foreground shadow-xs hover:bg-border-subtle hover:text-foreground active:bg-background active:text-muted-foreground disabled:bg-disabled disabled:text-disabled-foreground",
        ghost:
          "text-muted-foreground hover:bg-border-subtle hover:text-foreground active:bg-background active:text-muted-foreground disabled:text-disabled-foreground",
        link: "text-brand-dull !px-0 disabled:text-brand-muted underline underline-offset-4 hover:text-brand active:text-brand-dull/80",
        outline: "border-border-subtle border",
      },
      size: {
        default: "h-9 px-4 py-2 has-[>svg]:px-3",
        sm: "h-8 rounded-md gap-1.5 px-3 has-[>svg]:px-2.5",
        lg: "h-10 rounded-md px-6 has-[>svg]:px-4",
        icon: "size-9",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

export type ButtonVariants = VariantProps<typeof buttonVariants>;
