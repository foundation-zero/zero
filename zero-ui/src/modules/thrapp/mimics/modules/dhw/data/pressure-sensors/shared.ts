import { TooltipContent } from "@/modules/thrapp/components/tooltip";

export const tooltip = (content: Partial<TooltipContent>): TooltipContent => ({
  title: "Pressure sensor",
  itemName: "Pressure sensor",
  ...content,
});
