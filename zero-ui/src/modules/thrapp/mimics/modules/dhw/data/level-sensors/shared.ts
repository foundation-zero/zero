import { TooltipContent } from "@/modules/thrapp/components/tooltip";

export const tooltip = (content: Partial<TooltipContent>): TooltipContent => ({
  title: "Level sensor",
  itemName: "Level sensor",
  ...content,
});
