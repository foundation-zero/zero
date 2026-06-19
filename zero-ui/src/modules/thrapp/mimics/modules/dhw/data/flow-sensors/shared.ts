import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { getField } from "@/modules/thrapp/mimics/providers";
import { ControlComponentType } from "@/modules/thrs/types";

export const tooltip = (content: Partial<TooltipContent>): TooltipContent => ({
  title: "Flow sensor",
  itemName: "Flow sensor",
  ...content,
});

export const pump = getField(ControlComponentType.Pump, "dhw", "dhwPump");
