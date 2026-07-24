import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { getField, ModuleField } from "@/modules/thrapp/mimics/providers";
import { ControlComponentType, SensorComponentType } from "@/modules/thrs/types";
import { fieldTooltip } from "../shared";

export const tooltip = (field: ModuleField<SensorComponentType>): TooltipContent =>
  fieldTooltip(field, {
    title: "Flow sensor",
    itemName: "Flow sensor",
  });

export const pump = getField(ControlComponentType.Pump, "dhw", "dhwPump");
