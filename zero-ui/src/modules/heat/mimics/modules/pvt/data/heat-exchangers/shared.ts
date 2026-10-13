import { TooltipContent } from "@/modules/heat/components/tooltip";

export const tooltip = (content: Partial<TooltipContent>): TooltipContent => ({
  title: "Exchange circuit",
  componentType: "Heat Exchanger",
  ...content,
});
