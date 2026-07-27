import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { ModuleField } from "@/modules/thrapp/mimics/providers";
import { SensorComponentType } from "@/modules/thrs/types";
import { fieldTooltip } from "../shared";

export const tooltip = (field: ModuleField<SensorComponentType>): TooltipContent =>
  fieldTooltip(field, {
    title: "Temperature sensor",
    itemName: "Temperature sensor Pt100 RTD",
  });
