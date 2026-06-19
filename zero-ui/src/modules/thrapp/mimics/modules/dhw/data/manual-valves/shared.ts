import { TooltipContent } from "@/modules/thrapp/components/tooltip";

export const tooltip = (content: Partial<TooltipContent>): TooltipContent => ({
  title: "Manual valve",
  itemName: "Manual valve",
  ...content,
});
