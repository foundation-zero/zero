import { TooltipContent } from "@/modules/thrapp/components/tooltip";
import { getField, ModuleField } from "@/modules/thrapp/mimics/providers";
import { ControlComponentType, SensorComponentType } from "@/modules/thrsim/types";
import { fieldTooltip } from "../shared";

export const tooltip = (field: ModuleField<SensorComponentType>): TooltipContent =>
  fieldTooltip(field, {
    title: "Flow sensor",
    componentType: "Flow sensor",
  });

export const pump = getField(ControlComponentType.Pump, "dhw", "dhwPump");
