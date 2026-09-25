import { TooltipContent } from "@/modules/thrapp/components/tooltip";

export const tooltip = (content: Partial<TooltipContent>): TooltipContent => ({
  title: "Exchange circuit",
  componentType: "Heat Exchanger",
  ...content,
});
