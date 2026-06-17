import { TooltipContent } from "@/modules/thrapp/components/tooltip";

export const tooltip = (content: Partial<TooltipContent>): TooltipContent => ({
  title: "Flow sensor",
  itemName: "Flow sensor",
  ...content,
});
