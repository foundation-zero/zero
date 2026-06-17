import { TooltipContent } from "@/modules/thrapp/components/tooltip";

export const tooltip = (content: Partial<TooltipContent>): TooltipContent => ({
  title: "Temperature sensor",
  itemName: "Temperature sensor",
  ...content,
});
