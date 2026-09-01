import { TooltipContent } from "@/modules/thrapp/components/tooltip";

export const tooltip = (content: Partial<TooltipContent>): TooltipContent => ({
  title: "Heat Exchanger",
  componentType: "Heat Exchanger",
  ...content,
});
