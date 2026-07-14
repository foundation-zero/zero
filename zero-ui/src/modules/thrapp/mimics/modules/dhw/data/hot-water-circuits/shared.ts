import { TooltipContent } from "@/modules/thrapp/components/tooltip";

export const tooltip = (content: Partial<TooltipContent>): TooltipContent => ({
  title: "Connecting circuit",
  itemName: "Connecting circuit",
  ...content,
});
