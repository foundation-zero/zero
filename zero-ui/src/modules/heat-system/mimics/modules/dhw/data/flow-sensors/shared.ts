import { TooltipContent } from "@/modules/heat-system/components/tooltip";
import { getField, ModuleField } from "@/modules/heat-system/mimics/providers";
import { ControlComponentType, SensorComponentType } from "@/modules/heat-system-simulation/types";
import { fieldTooltip } from "../../../shared";

export const tooltip = (field: ModuleField<SensorComponentType>): TooltipContent =>
  fieldTooltip(field, {
    title: "Flow sensor",
    componentType: "Flow sensor",
  });

export const pump = getField(ControlComponentType.Pump, "dhw", "dhwPump");
