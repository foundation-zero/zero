import { TooltipContent } from "@/modules/thrapp/components/tooltip";

export const tooltip = (content: Partial<TooltipContent>): TooltipContent => ({
  title: "Hot water circuit",
  itemName: "Hot water circuit",
  ...content,
});
