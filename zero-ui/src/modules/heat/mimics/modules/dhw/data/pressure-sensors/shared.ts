import { TooltipContent } from "@/modules/heat/components/tooltip";
import { ModuleField } from "@/modules/heat/mimics/providers";
import { SensorComponentType } from "@/modules/heat-simulation/types";
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
