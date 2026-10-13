import { TooltipContent } from "@/modules/heat-system/components/tooltip";
import { ModuleField } from "@/modules/heat-system/mimics/providers";
import { SensorComponentType } from "@/modules/heat-system-simulation/types";
import { fieldTooltip } from "../../../shared";

export const tooltip = (
  field: ModuleField<SensorComponentType>,
  content?: Partial<TooltipContent>,
): TooltipContent =>
  fieldTooltip(field, {
    title: "Pressure sensor",
    componentType: "Pressure sensor",
    ...content,
  });
