import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { getField } from "@/modules/thrapp/mimics/providers";
import { ControlComponentType } from "@/modules/thrs/types";

export const tooltip = (content: Partial<TooltipContent>): TooltipContent => ({
  title: "Flow Control valve",
  itemName: "2 way valve DN 25",
  ...content,
});

export const actuator = getField(ControlComponentType.Pump, "dhw", "dhwPump");
