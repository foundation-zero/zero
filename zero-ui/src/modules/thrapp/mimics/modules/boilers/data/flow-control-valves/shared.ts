import { TooltipContent } from "@/modules/thrapp/components/tooltip";

export const tooltip = (content: Partial<TooltipContent>): TooltipContent => ({
  title: "Flow Control valve",
  itemName: "2 way valve DN 25",
  ...content,
});

export const setpointName = "boilers_filling_temperature";
